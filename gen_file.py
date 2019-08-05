import argparse
import numpy as np

from merge_sort import FileWriter, B, ALPHABET


def get_random_string(max_len):
    line_len = np.random.randint(0, max_len + 1)
    return ''.join(np.random.choice(ALPHABET, line_len))


def generate(output_filename, max_len, lines_count):
    with open(output_filename, 'a') as output_file:
        writer = FileWriter(output_file, B)
        for i in range(lines_count):
            s = get_random_string(max_len)
            writer.write(s)
        writer.flush()


def main():
    parser = argparse.ArgumentParser(description='''
    generate big random files of strings in small english letters.''')
    parser.add_argument('--output', type=str, help='name of file to generate', required=True)
    parser.add_argument('--max', type=str, help='maximal length of string', required=True)
    parser.add_argument('--count', type=str, help='number of lines', required=True)

    args = parser.parse_args()
    output_filename, max_len, lines_count = args.output,  args.max, args.count
    generate(output_filename, max_len, lines_count)


if __name__ == '__main__':
    main()