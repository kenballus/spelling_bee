import curses
import sys
import argparse
import locale
import pathlib

MAX_WORD_LENGTH: int = 30
MIN_WORD_LENGTH: int = 4
WORD_LIST_PATH_STR: str = "/usr/share/dict/american-english"
WORD_LIST_PATH: pathlib.PosixPath = pathlib.PosixPath(WORD_LIST_PATH_STR)

def error_out(error_message: str):
    print(f"Error: {error_message}", file=sys.stderr)
    sys.exit(1)

def validate_args(pangram: str, required_letter: str) -> None:
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
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Clone of NYTimes Spelling Bee')
    parser.add_argument('--pangram', required=True)
    parser.add_argument('--required_letter', metavar="CHARACTER", required=True)

    args: argparse.Namespace = parser.parse_args()

    pangram: str = args.pangram.lower()
    required_letter: str = args.required_letter.lower()

    validate_args(pangram, required_letter)

    with open("/usr/share/dict/american-english") as word_file:
        # Filter out all the words with symbols and uppercase letters, then save them
        valid_words: Set[str] = set(filter(lambda w: w.islower() and MIN_WORD_LENGTH <= len(w) <= MAX_WORD_LENGTH and set(w).issubset(set(pangram)),
                                           map(str.strip,
                                               word_file.readlines())))

    # If you really want a fake word, I'm cool with it.
    valid_words.add(pangram)

    stdscr = curses.initscr()
    curses.noecho()

    words_found = set()
    wip: str = ""
    score: int = 0
    while True:
        char: str = stdscr.getkey()

        if char.isalpha():
            wip += char.lower()
        elif char == '\n':
            if wip in valid_words:
                words_found.add(wip)
                score += (1 if len(wip) == MIN_WORD_LENGTH else len(wip))
                if set(wip) == set(pangram):
                    score += 7

            wip = ""
        elif char == '\x7f':
            wip = wip[:-1]

        stdscr.clear()
        maxy, maxx = stdscr.getmaxyx()
        stdscr.addstr(maxy // 2, (maxx - len(wip)) // 2, wip)
        stdscr.addstr(0, 0, " ".join(words_found))
        stdscr.addstr(maxy - 1, 0, str(score))

if __name__ == "__main__":
    main()
