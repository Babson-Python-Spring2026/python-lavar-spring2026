import random
from collections import deque


def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
        except ValueError:
            pass
        prompt = f"please enter an integer between {min_val} and {max_val} :"


def build_board(height, width, num_mines):
    all_cells = [(r, c) for r in range(height) for c in range(width)]
    mines = set(map(tuple, random.sample(all_cells, num_mines)))
    counts = [[0] * width for _ in range(height)]
    for r in range(height):
        for c in range(width):
            if (r, c) in mines:
                counts[r][c] = -1
            else:
                counts[r][c] = sum(
                    1 for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr, dc) != (0, 0) and (r + dr, c + dc) in mines
                )
    return counts


def display_board(height, width, counts, revealed, game_over=False):
    print("   " + "    ".join(str(c) for c in range(width)))
    sep = "    " + "- " * (width * 2 + 1)
    for r in range(height):
        print(sep)
        row_str = f"  {r} |"
        for c in range(width):
            if game_over or revealed[r][c]:
                if counts[r][c] == -1:
                    cell = " 💣 "
                elif counts[r][c] == 0:
                    cell = "    "
                else:
                    cell = f" {counts[r][c]}  "
            else:
                cell = " ♦  "
            row_str += cell + "|"
        print(row_str)
    print(sep)


def flood_reveal(height, width, counts, revealed, start_row, start_col):
    queue = deque([(start_row, start_col)])
    while queue:
        r, c = queue.popleft()
        if revealed[r][c]:
            continue
        revealed[r][c] = True
        if counts[r][c] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr, dc) != (0, 0):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < height and 0 <= nc < width and not revealed[nr][nc]:
                            queue.append((nr, nc))


def check_win(height, width, counts, revealed):
    for r in range(height):
        for c in range(width):
            if counts[r][c] != -1 and not revealed[r][c]:
                return False
    return True


def main():
    height = get_int_input("Board height (2 - 10): ", 2, 10)
    width = get_int_input("Board width (2 - 10): ", 2, 10)
    num_mines = get_int_input(f"How many mines (less than {height * width}): ", 1, height * width - 1)

    counts = build_board(height, width, num_mines)
    revealed = [[False] * width for _ in range(height)]

    while True:
        display_board(height, width, counts, revealed)
        col = get_int_input("How many over would you like to dig? ", 0, width - 1)
        row = get_int_input("How many down would you like to dig? ", 0, height - 1)

        if counts[row][col] == -1:
            display_board(height, width, counts, revealed, game_over=True)
            break

        flood_reveal(height, width, counts, revealed, row, col)

        if check_win(height, width, counts, revealed):
            display_board(height, width, counts, revealed, game_over=True)
            print("Congratulations! You won.")
            break


if __name__ == "__main__":
    main()
