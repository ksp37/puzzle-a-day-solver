def build_grid(solution, not_allowed, traverse_row):
    """
    Convert the DLX solution into a 7×7 grid where each cell holds a
    piece-index label (49-63 = piece columns) or a special marker.

    Returns:
        grid        – 7×7 list, each cell is a string label
        piece_colours – maps piece_idx -> ANSI colour string
        reset       – ANSI reset string
    """
    EMPTY   = "·"
    BLOCKED = "██"

    grid = [[EMPTY] * 7 for _ in range(7)]

    for (r, c) in not_allowed:
        grid[r][c] = BLOCKED

    ANSI_COLORS = [
        "\033[41m",  "\033[42m",  "\033[43m",  "\033[44m",
        "\033[45m",  "\033[46m",  "\033[101m", "\033[102m",
        "\033[103m", "\033[104m", "\033[105m", "\033[106m",
        "\033[48;5;214m", "\033[48;5;93m", "\033[48;5;36m",
    ]
    RESET = "\033[0m"

    piece_colours = {}
    colour_idx    = 0

    for row_elem in solution:
        row_numdes = traverse_row(row_elem)
        coords    = [n.coord for n in row_numdes]

        cell_coords  = [c for c in coords if c < 49]
        piece_coords = [c for c in coords if c >= 49]

        if not piece_coords:
            continue  # NOT_ALLOWED filler row

        piece_idx = piece_coords[0]
        if piece_idx not in piece_colours:
            piece_colours[piece_idx] = ANSI_COLORS[colour_idx % len(ANSI_COLORS)]
            colour_idx += 1

        label = f"P{piece_idx - 48:02d}"
        for flat in cell_coords:
            r, c = divmod(flat, 7)
            grid[r][c] = label

    return grid, piece_colours, RESET


def print_grid(grid, piece_colours, reset):
    """Pretty-print the 7×7 solution grid to the terminal with ANSI colours."""
    BLOCKED = "██"
    EMPTY   = "·"

    label_colour = {}
    for piece_idx, colour in piece_colours.items():
        label_colour[f"P{piece_idx - 48:02d}"] = colour

    print("    " + "  ".join(str(c) for c in range(7)))
    print("   " + "─" * (7 * 4))

    for r, row in enumerate(grid):
        line = f"{r} │ "
        for cell in row:
            if cell == BLOCKED:
                line += "\033[90m██\033[0m  "
            elif cell == EMPTY:
                line += f"{EMPTY}   "
            else:
                colour = label_colour.get(cell, "")
                line += f"{colour} {cell[1:]} {reset} "
        print(line)

    print()
    print("Legend:")
    for piece_idx, colour in sorted(piece_colours.items()):
        label = f"P{piece_idx - 48:02d}"
        print(f"  {colour} {label} {reset}  piece column {piece_idx}")


def save_grid_image(grid, piece_colours, filepath="puzzle_solution.png"):
    """
    Save the solution as a PNG using Pillow (FOSS, HPND licence).
    Falls back gracefully if Pillow is not installed.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("(install pillow with: pip install pillow  — to also save a PNG image)")
        return

    BLOCKED = "██"
    EMPTY   = "·"
    CELL    = 80
    PADDING = 20
    SIZE    = 7
    IMG_W   = SIZE * CELL + PADDING * 2
    IMG_H   = SIZE * CELL + PADDING * 2

    PIECE_RGB = [
        (220, 80,  80),  (80, 180,  80),  (220, 200, 60),  (80, 100, 220),
        (180, 80, 180),  (60, 200, 200),  (240, 140,  40),  (100, 220, 140),
        (240, 200, 100), (100, 140, 240), (220, 120, 200),  (80, 220, 220),
        (240, 160,  80), (160,  80, 240), (60,  200, 140),
    ]

    label_rgb = {}
    for i, (piece_idx, _) in enumerate(sorted(piece_colours.items())):
        label_rgb[f"P{piece_idx - 48:02d}"] = PIECE_RGB[i % len(PIECE_RGB)]

    img  = Image.new("RGB", (IMG_W, IMG_H), (245, 245, 245))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except Exception:
        font = ImageFont.load_default()

    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            x0 = PADDING + c * CELL
            y0 = PADDING + r * CELL
            x1 = x0 + CELL - 2
            y1 = y0 + CELL - 2

            if cell == BLOCKED:
                draw.rectangle([x0, y0, x1, y1], fill=(50, 50, 50))
            elif cell == EMPTY:
                draw.rectangle([x0, y0, x1, y1], fill=(200, 200, 200), outline=(180, 180, 180))
            else:
                rgb = label_rgb.get(cell, (200, 200, 200))
                draw.rectangle([x0, y0, x1, y1], fill=rgb, outline=(255, 255, 255), width=2)
                draw.text((x0 + 5, y0 + 5), cell, fill=(30, 30, 30), font=font)

    img.save(filepath)
    print(f"Solution image saved to: {filepath}")


def visualise(solution, not_allowed, traverse_row, filepath="puzzle_solution.png"):
    """Render the solution: print coloured grid to terminal and save a PNG."""
    grid, piece_colours, reset = build_grid(solution, not_allowed, traverse_row)
    print("\n── Puzzle Solution ─────────────────────────────────────────────\n")
    print_grid(grid, piece_colours, reset)
    save_grid_image(grid, piece_colours, filepath)
