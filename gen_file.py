import argparse
import numpy as np
import os
import time

from merge_sort import FileWriter, B, ALPHABET


def get_random_string(max_len):
    line_len = np.random.randint(0, max_len + 1)
    return ''.join(np.random.choice(ALPHABET, line_len))


def generate(output_filename, max_len, lines_count):
    if os.path.exists(output_filename):
        os.remove(output_filename)
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
    parser.add_argument('--max', type=int, help='maximal length of string', required=True)
    parser.add_argument('--count', type=int, help='number of lines', required=True)

    args = parser.parse_args()
    output_filename, max_len, lines_count = args.output,  args.max, args.count
    start = time.time()
    generate(output_filename, max_len, lines_count)
    end = time.time()
    print('time of work is %s seconds' % end - start)



if __name__ == '__main__':
    main()