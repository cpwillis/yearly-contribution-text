#!/usr/bin/env python3
import subprocess
import datetime
import sys
from typing import List

# Complete CHAR_MAP for a-z and 0-9
CHAR_MAP = {
    "a": ["0110", "1001", "1111", "1001", "1001", "0000", "0000"],
    "b": ["1110", "1001", "1110", "1001", "1110", "0000", "0000"],
    "c": ["0111", "1000", "1000", "1000", "0111", "0000", "0000"],
    "d": ["1110", "1001", "1001", "1001", "1110", "0000", "0000"],
    "e": ["1111", "1000", "1110", "1000", "1111", "0000", "0000"],
    "f": ["1111", "1000", "1110", "1000", "1000", "0000", "0000"],
    "g": ["0111", "1000", "1011", "1001", "0111", "0000", "0000"],
    "h": ["1001", "1001", "1111", "1001", "1001", "0000", "0000"],
    "i": ["111", "010", "010", "010", "111", "000", "000"],
    "j": ["0011", "0001", "0001", "1001", "0110", "0000", "0000"],
    "k": ["1001", "1010", "1100", "1010", "1001", "0000", "0000"],
    "l": ["1000", "1000", "1000", "1000", "1111", "0000", "0000"],
    "m": ["10001", "11011", "10101", "10001", "10001", "00000", "00000"],
    "n": ["1001", "1101", "1011", "1001", "1001", "0000", "0000"],
    "o": ["0110", "1001", "1001", "1001", "0110", "0000", "0000"],
    "p": ["1110", "1001", "1110", "1000", "1000", "0000", "0000"],
    "q": ["0110", "1001", "1001", "1011", "0111", "0000", "0000"],
    "r": ["1110", "1001", "1110", "1010", "1001", "0000", "0000"],
    "s": ["0111", "1000", "0110", "0001", "1110", "0000", "0000"],
    "t": ["11111", "00100", "00100", "00100", "00100", "00000", "00000"],
    "u": ["1001", "1001", "1001", "1001", "0110", "0000", "0000"],
    "v": ["1001", "1001", "1001", "0101", "0010", "0000", "0000"],
    "w": ["10001", "10001", "10101", "11011", "10001", "00000", "00000"],
    "x": ["1001", "0101", "0010", "0101", "1001", "0000", "0000"],
    "y": ["1001", "0101", "0010", "0010", "0010", "0000", "0000"],
    "z": ["1111", "0001", "0010", "0100", "1111", "0000", "0000"],
    "0": ["0110", "1001", "1001", "1001", "0110", "0000", "0000"],
    "1": ["010", "110", "010", "010", "111", "000", "000"],
    "2": ["0110", "1001", "0010", "0100", "1111", "0000", "0000"],
    "3": ["1110", "0001", "0110", "0001", "1110", "0000", "0000"],
    "4": ["1001", "1001", "1111", "0001", "0001", "0000", "0000"],
    "5": ["1111", "1000", "1110", "0001", "1110", "0000", "0000"],
    "6": ["0111", "1000", "1110", "1001", "0110", "0000", "0000"],
    "7": ["1111", "0001", "0010", "0100", "0100", "0000", "0000"],
    "8": ["0110", "1001", "0110", "1001", "0110", "0000", "0000"],
    "9": ["0110", "1001", "0111", "0001", "1110", "0000", "0000"],
}


def get_char_width(char: str) -> int:
    """Get the actual width of a character from CHAR_MAP."""
    char_bitmap = CHAR_MAP.get(char.lower())
    return len(char_bitmap[0]) if char_bitmap else 0


def get_max_chars(
    graph_width: int = 52, avg_char_width: int = 4, spacing: int = 1
) -> int:
    """Calculate maximum characters that fit in the graph width.

    Note: This is an estimate since character widths vary (3-5 columns).
    """
    return graph_width // (avg_char_width + spacing)


def generate_commit(date: str) -> bool:
    """Create a dummy commit on a specific date.

    Returns:
        True if commit was successful, False otherwise.
    """
    result = subprocess.run(
        ["git", "commit", "--allow-empty", "-m", f"Commit for {date}", "--date", date],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def build_bitmap(text: str) -> List[str]:
    """Return a 7-row bitmap for the entire string.

    Args:
        text: Input string (only a-z and 0-9 are rendered)

    Returns:
        List of 7 strings representing the bitmap rows
    """
    text = text.lower()
    max_chars = get_max_chars()
    text = text[:max_chars]

    bitmap_rows = [""] * 7
    total_width = 0

    for char in text:
        char_bitmap = CHAR_MAP.get(char)
        if not char_bitmap:
            print(
                f"Warning: Character '{char}' not supported, skipping.", file=sys.stderr
            )
            continue

        # Check if adding this character would exceed graph width
        char_width = len(char_bitmap[0]) + 1  # +1 for spacing
        if total_width + char_width > 52:
            print(
                f"Warning: Text truncated at '{char}' to fit 52-week graph.",
                file=sys.stderr,
            )
            break

        for i in range(7):
            bitmap_rows[i] += char_bitmap[i] + "0"  # Add 1-column spacing
        total_width += char_width

    # Shift everything down by adding an empty row at the top
    bitmap_rows = ["0" * len(bitmap_rows[0])] + bitmap_rows[:-1]

    return bitmap_rows


def preview_bitmap(bitmap_rows: List[str]) -> None:
    """Print bitmap in terminal using █ for commits and space for empty."""
    print("\nPreview (7 rows × width):")
    for row in bitmap_rows:
        print("".join("█" if c == "1" else " " for c in row))
    print(f"\nTotal width: {len(bitmap_rows[0])} columns (max: 52)\n")


def write_string_to_git(text: str, year: int) -> None:
    """Generate git commits to form text in contribution graph.

    Args:
        text: The text to render
        year: The year to generate commits for
    """
    # Validate year
    if year < 2000 or year > 2100:
        print(
            f"Error: Year {year} seems unusual. Please use a year between 2000-2100.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Check if we're in a git repository
    result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
    if result.returncode != 0:
        print("Error: Not in a git repository. Run 'git init' first.", file=sys.stderr)
        sys.exit(1)

    bitmap_rows = build_bitmap(text)

    # Find first Sunday of the year
    d = datetime.date(year, 1, 1)
    while d.weekday() != 6:
        d += datetime.timedelta(days=1)

    total_commits = sum(row.count("1") for row in bitmap_rows)
    commit_count = 0
    failed_commits = 0

    print(f"Generating {total_commits} commits for '{text}' in {year}...")

    for col in range(len(bitmap_rows[0])):
        for row in range(7):
            if bitmap_rows[row][col] == "1":
                commit_date = d + datetime.timedelta(days=row + col * 7)
                if generate_commit(commit_date.strftime("%Y-%m-%dT12:00:00")):
                    commit_count += 1
                    if commit_count % 10 == 0 or commit_count == total_commits:
                        print(
                            f"Progress: {commit_count}/{total_commits} commits",
                            end="\r",
                        )
                else:
                    failed_commits += 1

    print(f"\nCompleted: {commit_count} commits generated", end="")
    if failed_commits > 0:
        print(f" ({failed_commits} failed)", end="")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Write a string to GitHub contributions."
    )
    parser.add_argument(
        "text", type=str, help="Text to display in the contribution graph (a-z, 0-9)."
    )
    parser.add_argument("year", type=int, help="Year for the contributions.")
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the bitmap instead of creating commits.",
    )
    args = parser.parse_args()

    # Validate input text
    valid_chars = set(CHAR_MAP.keys())
    invalid_chars = [c for c in args.text.lower() if c not in valid_chars]
    if invalid_chars:
        print(f"Warning: Unsupported characters will be skipped: {set(invalid_chars)}")

    bitmap = build_bitmap(args.text)

    if not any(bitmap):  # Check if bitmap is empty
        print("Error: No valid characters to render.", file=sys.stderr)
        sys.exit(1)

    if args.preview:
        preview_bitmap(bitmap)
    else:
        write_string_to_git(args.text, args.year)
