import argparse

parser = argparse.ArgumentParser(prog="Fibonacci Generator")
parser.add_argument(
    "-c",
    "--count",
    help="How many numbers to print. Must be greater than or equal to 1.",
    required=True,
    type=int,
)
parser.add_argument(
    "--one-line",
    action="store_true",
    help="Print all of the numbers on one line separated by commas, rather than each on a new line",
)
parser.add_argument(
    "--numbering",
    action="store_true",
    help="Preface each number in the sequence with its placement:",
)
parser.add_argument(
    "--last-only",
    action="store_true",
    help="Only print the last number of the sequence",
)
args = parser.parse_args()

if args.count < 1:
    parser.error("Count must be greater than or equal to 1")


def calculate(n: int):
    """Calculate fibonacci numbers

    Args:
        n (int): How many to generate

    Returns:
        list: Calculated fibonacci numbers
    """
    if n == 1:
        return [0]

    sequence = [0, 1]
    for i in range(n - 2):
        sequence.append(sequence[-1] + sequence[-2])

    return sequence


def print_result(numbers: list):
    """Prints a list of numbers formatted based on program arguments

    Args:
        numbers (list): A list of numbers to format and print
    """
    if args.numbering:
        for i in range(len(numbers)):
            numbers[i] = f"{i + 1}:{numbers[i]}"

    if args.last_only:
        print(numbers[-1])
    else:
        print((", " if args.one_line else "\n").join(map(str, numbers)))


print_result(calculate(args.count))
