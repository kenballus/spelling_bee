import curses
import sys
import argparse
import locale
import pathlib
import random
from typing import Set, List

MAX_WORD_LENGTH: int = 30
MIN_WORD_LENGTH: int = 4
WORD_LIST_PATH_STR: str = "/usr/share/dict/american-english"
WORD_LIST_PATH: pathlib.PosixPath = pathlib.PosixPath(WORD_LIST_PATH_STR)


def error_out(error_message: str) -> None:
    print(f"Error: {error_message}", file=sys.stderr)
    sys.exit(1)


def check_for_errors(letters: str, required_letter: str) -> None:
    if not WORD_LIST_PATH.is_file():
        error_out(f"No word list found at {WORD_LIST_PATH_STR}.")

    if len(required_letter) != 1:
        error_out("The required letter is more than one character.")

    if not required_letter.isalpha():
        error_out("The required letter is not a letter.")

    if not letters.isalpha():
        error_out("The letters contains non-letters.")

    if required_letter not in letters:
        error_out("The required letter is not in the letters.")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Clone of NYTimes Spelling Bee"
    )
    parser.add_argument("--letters", required=True)
    parser.add_argument("--required_letter", metavar="LETTER", required=True)

    args: argparse.Namespace = parser.parse_args()

    letters: str = args.letters.lower()
    required_letter: str = args.required_letter.lower()

    # This may exit the program
    check_for_errors(letters, required_letter)

    valid_letters: Set[str] = set(letters)

    with open(WORD_LIST_PATH) as word_file:
        # Filter out all the words with symbols and uppercase letters, then save them
        valid_words: Set[str] = set(
            filter(
                lambda w: w.islower()
                and MIN_WORD_LENGTH <= len(w) <= MAX_WORD_LENGTH
                and required_letter in w
                and set(w).issubset(valid_letters),
                map(str.strip, word_file.readlines()),
            )
        )

    stdscr = curses.initscr()
    curses.noecho()
    curses.curs_set(False)

    words_found: List[str] = []
    wip: str = ""
    score: int = 0

    letter_arrangement: str = "".join(valid_letters)
    required_letter_index: int = letter_arrangement.index(required_letter)

    while True:
        maxy, maxx = stdscr.getmaxyx()
        stdscr.clear()

        if maxx <= MAX_WORD_LENGTH:
            stdscr.addstr(0, 0, "Terminal too small!")
        else:
            # Word in progress (middle)
            stdscr.addstr(maxy // 2, (maxx - len(wip)) // 2, wip)
            # Words found (top)
            stdscr.addstr(0, 0, " ".join(words_found))
            # Score (bottom left)
            stdscr.addstr(maxy - 1, 0, f"score: {score}")
            # Available letters (just above middle)
            stdscr.addstr(
                maxy // 2 - 1,
                (maxx - len(letter_arrangement)) // 2,
                letter_arrangement[:required_letter_index],
                curses.A_BOLD,
            )
            stdscr.addstr(
                maxy // 2 - 1,
                (maxx - len(letter_arrangement)) // 2 + required_letter_index,
                required_letter,
                curses.A_BOLD | curses.A_UNDERLINE,
            )
            stdscr.addstr(
                maxy // 2 - 1,
                (maxx - len(letter_arrangement)) // 2 + required_letter_index + 1,
                letter_arrangement[required_letter_index + 1 :],
                curses.A_BOLD,
            )
            # Progress (bottom right)
            progress_str = f"{len(words_found)}/{len(valid_words)} words found"
            stdscr.addstr(maxy - 1, maxx - 1 - len(progress_str), progress_str)

        # Actually get a key.
        # This is a blocking action.
        # If they press ctrl-c, quit.
        try:
            char: str = stdscr.getkey().lower()
        except KeyboardInterrupt:
            break

        if char.isalpha():
            wip += char
            if len(wip) > MAX_WORD_LENGTH:
                wip = ""
        elif char == "\n":
            if required_letter in wip and wip in valid_words and wip not in words_found:
                words_found.append(wip)
                words_found.sort()
                score += 1 if len(wip) == MIN_WORD_LENGTH else len(wip)
                if set(wip) == valid_letters:
                    score += 7
            wip = ""
        elif char == " ":
            l: List[str] = list(letter_arrangement)
            random.shuffle(l)
            letter_arrangement = "".join(l)
            required_letter_index = letter_arrangement.index(required_letter)
        elif char == "\x7f":  # Backspace
            wip = wip[:-1]
        elif char == "\x04":  # Ctrl-D
            break

    quit_curses()


def quit_curses() -> None:
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    main()
