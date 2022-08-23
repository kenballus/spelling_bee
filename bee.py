import curses
import sys
import argparse
import locale
import pathlib
import random

MAX_WORD_LENGTH: int = 30
MIN_WORD_LENGTH: int = 4
WORD_LIST_PATH_STR: str = "/usr/share/dict/american-english"
WORD_LIST_PATH: pathlib.PosixPath = pathlib.PosixPath(WORD_LIST_PATH_STR)


def error_out(error_message: str) -> None:
    print(f"Error: {error_message}", file=sys.stderr)
    sys.exit(1)


def check_for_errors(pangram: str, required_letter: str) -> None:
    if not WORD_LIST_PATH.is_file():
        error_out(f"Cannot find a word list at {WORD_LIST_PATH_STR}.")

    if len(required_letter) != 1:
        error_out("The required letter is more than one character.")

    if not required_letter.isalpha():
        error_out("The required letter is not a letter.")

    if not pangram.isalpha():
        error_out("The pangram contains non-letters.")

    if required_letter not in pangram:
        error_out("The required letter is not in the pangram.")


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Clone of NYTimes Spelling Bee"
    )
    parser.add_argument("--pangram", required=True)
    parser.add_argument("--required_letter", metavar="LETTER", required=True)

    args: argparse.Namespace = parser.parse_args()

    pangram: str = args.pangram.lower()
    required_letter: str = args.required_letter.lower()

    # This may exit the program
    check_for_errors(pangram, required_letter)

    valid_letters: Set[str] = set(pangram)

    with open("/usr/share/dict/american-english") as word_file:
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

    # If you really want a fake word, I'm cool with it.
    valid_words.add(pangram)

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

        if maxx < MAX_WORD_LENGTH:
            stdscr.addstr(0, 0, "Terminal too small!")
        else:
            stdscr.addstr(maxy // 2, (maxx - len(wip)) // 2, wip)
            stdscr.addstr(0, 0, " ".join(words_found))
            stdscr.addstr(maxy - 1, 0, f"score: {score}")
            stdscr.addstr(
                maxy // 2 - 1,
                (maxx - len(letter_arrangement)) // 2,
                letter_arrangement[:required_letter_index],
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
            )

        char: str = stdscr.getkey().lower()

        if char.isalpha():
            wip += char
            if len(wip) > MAX_WORD_LENGTH:
                wip = ""
        elif char == "\n":
            if required_letter in wip and wip in valid_words and wip not in words_found:
                words_found.append(wip)
                words_found.sort()
                score += 1 if len(wip) == MIN_WORD_LENGTH else len(wip)
                if set(wip) == set(pangram):
                    score += 7
            wip = ""
        elif char == " ":
            l: List[str] = list(letter_arrangement)
            random.shuffle(l)
            letter_arrangement = "".join(l)
            required_letter_index: int = letter_arrangement.index(required_letter)
        elif char == "\x7f":
            wip = wip[:-1]


if __name__ == "__main__":
    main()
