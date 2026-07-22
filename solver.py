from visualisation import visualise

NOT_ALLOWED = {
    (0,6),
    (1,6),
    (6,3),
    (6,4),
    (6,5),
    (6,6),
    (1,0), # July
    (5,0) # 22nd
}

primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113,
    127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
    179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
    283, 293, 307, 311, 313, 317, 331, 337, 347, 349
]

class Node:
    def __init__(self):
        self.coord = None
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.header = None
        self.row_num = None

    def __repr__(self):
        return f"coord: {self.coord}, left: {self.left.coord}, right: {self.right.coord}, id {id(self)}, top id {id(self.top)}, bottom id {id(self.bottom)}, header {self.header.count}"

class HeaderNode:
    def __init__(self, coord):
        self.coord = coord
        self.count = 0
        self.deleted = False
        self.node = None

def set_up_matrix(permutations):
    matrix = []
    # Each row corresponds to a given shape in a position
    for permutation in permutations:
        matrix.append([1 if coord in permutation else 0 for coord in range(49)])

    # Certain coordinates are not allowed to be occupied by shapes 
    # A single row will represent this constraint and must form part of the solution
    not_allowed_flattened = flatten_coords(NOT_ALLOWED)
    matrix.append([1 if coord in not_allowed_flattened else 0 for coord in range(49)])
    return matrix

def set_up_links(permutations, no_cols):
    # Create empty matrix and headers
    matrix = [[] for _ in range(no_cols)]
    headers = [HeaderNode(idx) for idx in range(no_cols) ]
    # Each permutation will correspond to a row
    for row_num, permutation in enumerate(permutations):
        left_node = None
        # For each coord in the permutation, create a node and link it
        # to the left, right, top and bottom neighbours. 
        for coord in permutation:
            node = Node()
            node.coord = coord
            node.row_num = row_num

            # Link neighbours at the top and bottom
            if len(matrix[coord]):
                node.top = matrix[coord][-1]
                matrix[coord][-1].bottom = node
            matrix[coord].append(node)

            # Link node to header and vice versa
            node.header = headers[coord]
            headers[coord].node = node
            headers[coord].count += 1

            # Link left and right neighbours
            if left_node:
                left_node.right = node
                node.left = left_node
            else:
                # if there is no left neighbour, this must be the first node
                first_node = node

            left_node = node

        # Link the right most node and the left most node
        node.right = first_node
        first_node.left = node
    
    # Link the top most node and the bottom most node
    for idx, col in enumerate(matrix):
        if headers[idx].count > 0:
            col[-1].bottom = col[0]
            col[0].top = col[-1]

    return matrix, headers

def calculate_key(perm):
    # Use the fundamental theorem of arithmetic to calculate a unique key
    # for each shape permutation
    key = 1
    for coord in perm:
        key *= primes[coord]
    return key


def delete_nodes(nodes):
    for node in nodes:
        node.left.right = node.right
        node.right.left = node.left
        node.top.bottom = node.bottom
        node.bottom.top = node.top
        node.header.node = node.top
        node.header.count -= 1

def add_nodes(nodes):
    for node in nodes:
        node.left.right = node
        node.right.left = node
        node.top.bottom = node
        node.bottom.top = node
        node.header.count += 1

def traverse_column(original_node):
    column = [original_node]
    node = original_node.bottom
    while node != original_node:
        column.append(node)
        node = node.bottom
    
    return column

def traverse_row(original_node):
    row = [original_node]
    node = original_node.right
    while node != original_node:
        row.append(node)
        node = node.right
    
    return row

def dlx(headers, partial_solution):
    # Empty matrix, so must have found a solution
    if all(header.deleted for header in headers):
        return True

    # Find col with fewest elements
    min_header = min((header for header in headers if not header.deleted), key=lambda x : (x.count, x.coord))

    if min_header.count == 0:
        return False
    
    row_elem = min_header.node
    first_node = min_header.node
    
    ran_once = False
    while row_elem != first_node or ran_once is False:
        ran_once = True
        # Consider a row (shape in a given orientation) by removing it 
        # from the matrix and adding it to the temporary solution
        partial_solution.append(row_elem)
        nodes_to_delete = []
        rows_visited = set()
        # Get all nodes in the row
        row_numdes = traverse_row(row_elem)
        for row_numde in row_numdes:
            row_numde.header.deleted = True
            # For each row element, get the intersecting column
            col_nodes = traverse_column(row_numde)
            for col_node in col_nodes:
                if col_node.row_num not in rows_visited:
                    # Each row that intersects the column must be removed
                    nodes_to_delete.extend(traverse_row(col_node))
                    rows_visited.add(col_node.row_num)

        delete_nodes(nodes_to_delete)

        # Recurse with the modified matrix and new row in the partial solution
        result = dlx(headers, partial_solution)

        # Revert the matrix to its state at the beginning of the call 
        add_nodes(reversed(nodes_to_delete))

        if result is True:
            return True
                
        # If the recursion didn't succeed, remove the selected row from
        # the solution 
        partial_solution.pop()

        # Unmark the columns so they are no longer deleted
        for row_numde in row_numdes:
            row_numde.header.deleted = False

        # Move to the next row
        row_elem = row_elem.bottom

    return False


def rotate_90(origin, points):
    ox, oy = origin
    return [(ox + (y - oy), oy - (x - ox)) for (x, y) in points]

def flip_over_x(origin, original):
    permutation = [original[0]]
    for point in original[1:]:
        permutation.append((point[0], 2*origin[1] - point[1]))

    return permutation

def flip_over_y(origin, original):
    permutation = [original[0]]
    for point in original[1:]:
        permutation.append((2*origin[0] - point[0], point[1]))

    return permutation

def is_in_bounds(coords):
    for x,y in coords:
        if x < 0 or y < 0 or x > 6 or y > 6 or (x,y) in NOT_ALLOWED:
            return False
    return True

def two_bar(origin, idx):
    x, y = origin
    original = [(x, y), (x+1, y)]
    perms = create_permutations(origin, original)
    for perm in perms:
        perm.append(idx)

    return perms

def three_bar(origin, idx):
    x, y = origin
    original = [(x, y), (x+1, y), (x+2, y)]
    perms = create_permutations(origin, original)
    for perm in perms:
        perm.append(idx)

    return perms

def three_by_three(origin, idx):
    x, y = origin
    original = [(x, y), (x+1, y), (x+2, y), (x, y+1), (x+1, y+1), (x+2, y+1), (x, y+2), (x+1, y+2), (x+2, y+2)]
    perms = create_permutations(origin, original)
    for perm in perms:
        perm.append(idx)

    return perms

def six_by_six(origin, idx):
    x,y = origin
    original = []
    for x_idx in range(6):
        for y_idx in range(6):
            original.append((x+x_idx, y + y_idx))

    perms = create_permutations(origin, original)
    for perm in perms:
        perm.append(idx)

    return perms

def add_shape_id(perms, idx):
    for perm in perms:
        perm.append(idx)

    return perms

def rectange(origin, id):
    x, y = origin
    original = [(x, y), (x+1, y), (x+2, y), (x, y+1), (x+1, y+1), (x+2, y+1)]
    return add_shape_id(create_permutations(origin, original), id)

def lightning(origin, id):
    x, y = origin
    original = [(x, y), (x, y+1), (x, y+2), (x+1, y+2), (x+1, y+3)]
    return add_shape_id(create_permutations(origin, original), id)

def ell(origin, id):
    x, y = origin
    original = [(x,y), (x+1, y), (x+2, y), (x+2, y+1), (x+2, y+2)]
    return add_shape_id(create_permutations(origin, original), id)

def eff(origin, id):
    x, y = origin
    original = [(x,y), (x, y+1), (x, y+2), (x, y+3), (x+1, y+1)]
    return add_shape_id(create_permutations(origin, original), id)

def you(origin, id):
    x, y = origin
    original = [(x,y), (x+1, y), (x+1, y+1), (x+1, y+2), (x, y+2)]
    return add_shape_id(create_permutations(origin, original), id)

def zed(origin, id):
    x, y = origin
    original = [(x,y), (x, y+1), (x+1, y+1), (x+2, y+1), (x+2, y+2)]
    return add_shape_id(create_permutations(origin, original), id)

def arr(origin, id):
    x, y = origin
    original = [(x,y), (x, y+1), (x, y+2), (x, y+3), (x+1, y)]
    return add_shape_id(create_permutations(origin, original), id)

def pointer(origin, id):
    x, y = origin
    original = [(x,y), (x, y+1), (x+1, y), (x+1, y+1), (x, y+2)]
    return add_shape_id(create_permutations(origin, original), id)

def flatten_coords(permutation):
    return [7*x + y for x,y in permutation]


def create_permutations(origin, original):
    permutations = [original]
    permutations_x_flip = [flip_over_x(origin, original)]
    permutations_y_flip = [flip_over_y(origin, original)]

    for _ in range(3):
        permutations.append(rotate_90(origin, permutations[-1]))
        permutations_x_flip.append(rotate_90(origin, permutations_x_flip[-1]))
        permutations_y_flip.append(rotate_90(origin, permutations_y_flip[-1]))

    return [flatten_coords(permutation) for permutation in permutations + permutations_x_flip + permutations_y_flip if is_in_bounds(permutation)]

def print_matrix(matrix):
    for idx, col in enumerate(matrix):
        print(f"Column {idx}")
        for node in col:
            try:
                print(node)
            except:
                print("EXCEPTION")
                print(node.coord)

def shape_set_up():
    permutations = []
    for row in range(7):
        for col in range(7):
            origin = (row, col)
            permutations.extend(rectange(origin, 49))
            permutations.extend(lightning(origin, 50))
            permutations.extend(ell(origin, 51))
            permutations.extend(eff(origin, 52))
            permutations.extend(you(origin, 53))
            permutations.extend(zed(origin, 54))
            permutations.extend(arr(origin, 55))
            permutations.extend(pointer(origin, 56))

    permutations.extend([flatten_coords(NOT_ALLOWED)])
    return permutations

def test_set_up():
    permutations = []
    for row in range(7):
        for col in range(7):
            origin = (row, col)
            permutations.extend(two_bar(origin, 49))
            permutations.extend(two_bar(origin, 50))
            permutations.extend(two_bar(origin, 51))
            permutations.extend(two_bar(origin, 52))
            permutations.extend(three_bar(origin, 53))
            permutations.extend(three_bar(origin, 54))
            permutations.extend(three_bar(origin, 55))
            permutations.extend(three_bar(origin, 56))
            permutations.extend(three_bar(origin, 57))
            permutations.extend(three_bar(origin, 58))
            permutations.extend(three_bar(origin, 59))
            permutations.extend(three_bar(origin, 60))
            permutations.extend(three_bar(origin, 61))
            permutations.extend(three_bar(origin, 62))
            permutations.extend(three_bar(origin, 63))

            # permutations.extend(two_bar(origin, 49))
            # permutations.extend(two_bar(origin, 50))
            # permutations.extend(three_bar(origin, 51))
            # permutations.extend(three_by_three(origin, 52))
            # permutations.extend(three_by_three(origin, 53))
            # permutations.extend(three_by_three(origin, 54))
            # permutations.extend(three_by_three(origin, 55))


    permutations.extend([flatten_coords(NOT_ALLOWED)])
    return permutations


if __name__ == "__main__":
    origin = (0,0)
    perms = shape_set_up()
    duplicates = set()
    unique_perms = []
    for perm in perms:
        key = calculate_key(perm)
        if key not in duplicates:
            unique_perms.append(perm)
            duplicates.add(key)

    matrix, headers = set_up_links(unique_perms, 57)
    solution = []

    dlx(headers,solution)
    for row_elem in solution:
        row = traverse_row(row_elem)
        row = [row_elem.coord for row_elem in row]
        print(row)

    visualise(solution, NOT_ALLOWED, traverse_row)



