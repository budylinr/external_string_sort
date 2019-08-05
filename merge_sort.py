import argparse
from contextlib import ExitStack
import os
import uuid


ALPHABET = list('abcdefghijklmnopqrstuvwxyz')
LETTER_TO_POW = {x: 2 ** i for i, x in enumerate(ALPHABET)}
POW_TO_LETTER = {2 ** i: x for i, x in enumerate(ALPHABET)}

# M and B from Vitter model
M = 100
B = 4

class BitSet(object):
    def __init__(self):
        self.number = 0

    def add(self, letter):
        pow_two = LETTER_TO_POW[letter]
        self.number |= pow_two

    def get_min(self):
        return POW_TO_LETTER[self.number & (self.number ^ (self.number - 1))]

    def remove(self, letter):
        pow_two = LETTER_TO_POW[letter]
        self.number &= ~ pow_two


class TrieNode(object):
    def __init__(self, terminal_data):
        self.children_bit_set = BitSet()
        self.children = {}
        self.terminal_data = terminal_data

    def add_child(self, letter, child_node):
        self.children[letter] = child_node
        self.children_bit_set.add(letter)

    def delete_child(self, letter):
        del self.children[letter]
        self.children_bit_set.remove(letter)

    def add_word(self, new_word, word_cur, file_reader):
        if word_cur == len(new_word):
            self.terminal_data.append(file_reader)
            return
        letter = new_word[word_cur]
        if letter not in self.children:
            new_node = TrieNode([file_reader])
            self.add_child(letter, new_node)
            return
        else:
            child = self.children[letter]
            child.add_word(new_word, word_cur + 1, file_reader)
            return

    def pop_min(self):
        # condition near work only in root for empty words
        if self.terminal_data:
            return self.terminal_data.pop()
        else:
            min_letter = self.children_bit_set.get_min()
            min_child = self.children[min_letter]
            if min_child.terminal_data:
                res = min_child.terminal_data.pop()
                if not min_child.terminal_data and not min_child.children:
                    self.delete_child(min_letter)
                return res
            else:
                return min_child.pop_min()

    def is_empty(self):
        return len(self.children) == 0 and len(self.terminal_data) == 0


class FileReader(object):
    def __init__(self, file_handler, read_bytes, end_file):
        self.file_handler = file_handler
        self.buffer = []
        self.sum_len = 0
        self.read_bytes = read_bytes
        self.end_file = end_file
        self.file_exhausted = False
        self.fill_buffer()

    def fill_buffer(self):
        start_fragment = self.file_handler.tell()
        self.file_handler.seek(self.read_bytes, 1)
        self.file_handler.readline()
        end_fragment = self.file_handler.tell()
        chunk_size = end_fragment - start_fragment
        if chunk_size > 2 * self.read_bytes:
            raise MemoryError('string in file is bigger than read_bytes bytes')
        chunk = self.file_handler.read(chunk_size).decode()
        # invert lines to have smaller strings on the top of the buffer
        self.buffer = chunk.splitlines()[::-1]
        self.file_exhausted = end_fragment >= self.end_file

    def pop(self):
        res = self.buffer.pop()
        if not self.buffer:
            self.fill_buffer()
        return res, self.file_exhausted and not self.buffer


class FileWriter(object):
    def __init__(self, file_handler, buffer_size):
        self.file_handler = file_handler
        self.buffer_size = buffer_size
        self.total_len = 0
        self.buffer = []

    def flush(self):
        self.file_handler.write('\n'.join(self.buffer))
        self.buffer = []
        self.total_len = 0

    def write(self, word):
        self.buffer.append(word)
        self.total_len += len(word)
        if self.total_len > self.buffer_size:
            self.flush()


class FileManager(object):
    def __init__(self):
        self.tmp_file_names = {}
        self.other_file_names = set(os.listdir())

    def get_new_file_name(self, is_tmp):
        for i in range(10):
            unique_filename = str(uuid.uuid4())
            if unique_filename not in self.tmp_fnames and unique_filename not in self.other_file_names:
                self.tmp_fnames[unique_filename] = is_tmp
                return unique_filename
        else:
            raise Exception('can not find unique name')

    def close(self):
        for fname in self.tmp_file_names:
            if self.tmp_file_names[fname]:
                os.remove(fname)


def merge_sorted_files_in_one_file(fnames_list, file_manager):
    output_fname = file_manager.get_new_file_name(is_tmp=False)
    with open(output_fname, 'a') as output_file:
        with ExitStack() as stack:
            files = [stack.enter_context(open(fname)) for fname in fnames_list]
            file_sizes = [os.path.getsize(fname) for fname in fnames_list]
            file_readers = [FileReader(file, B, file_size) for file, file_size in zip(files, file_sizes)]
            trie = TrieNode()
            writer = FileWriter(output_file, B)
            for reader in file_readers:
                # we read words from reader but not pop them
                # because we pop the word at the moment when it is minimal in trie
                # and we can write it to output file
                for w in reader.buffer:
                    trie.add_word(w, 0, reader)
            num_reading_ends = 0
            while num_reading_ends < len(fnames_list):
                reader = trie.pop_min()
                word, reading_end = reader.pop()
                # reading_end = True can be only once for a reader
                if reading_end:
                    num_reading_ends += 1
                else:
                    trie.add_word(reader.pop())
                writer.write(word)
            writer.flush()


def merge_sorted_files(fnames_list, file_manager):
    # we want to merge k files in one file
    k = M // B
    output_fnames_list = []
    for i in range(0, len(fnames_list), k):
        batch_end = min(i + k, len(fnames_list))
        output_fnames_list.append(
            merge_sorted_files_in_one_file(fnames_list[i:batch_end], file_manager)
        )
    return output_fnames_list


def merge_phase(fnames_list, file_manager):
    while len(fnames_list) > 1:
        fnames_list = merge_sorted_files(fnames_list, file_manager)
    return fnames_list[0]


def sort_file_in_memory(input_file, file_manager):
    output_fname = file_manager.get_new_file_name(False)
    start_fragment = input_file.tell()
    input_file.seek(M, 1)
    input_file.readline()
    end_fragment = input_file.tell()
    chunk_size = end_fragment - start_fragment
    if chunk_size > M + B:
        raise MemoryError('string in file is bigger than B bytes')
    words = input_file.read(chunk_size).decode().splitlines()
    trie = TrieNode()
    for word in words:
        trie.add_word(word, 0, word)
    with open(output_fname, 'a') as output_file:
        writer = FileWriter(output_fname, B)
        while not trie.is_empty():
            writer.write(trie.pop_min())
        writer.flush()
    return output_fname


def get_sorted_chunks(input_file, file_size, file_manager):
    sorted_fnames = []
    while input_file.tell() < file_size:
        sorted_fnames.append(sort_file_in_memory(input_file, file_manager))
    return sorted_fnames


def sort_file(fname):
    file_manager = FileManager()
    with open(fname, 'rb') as input_file:
        fnames_list = get_sorted_chunks(input_file, os.path.getsize(fname), file_manager)
    output_fname = merge_phase(fnames_list, file_manager)
    return output_fname


def main():
    parser = argparse.ArgumentParser(description='''
    Sort big text files with strings in english small literals in external memory.''')
    parser.add_argument('--input', type=str, help='name of file to sort')
    args = parser.parse_args()
    input_file_name = args.input
    output_filename = sort_file(input_file_name)
    print('output_filename is %s' % output_filename)


if __name__ == '__main__':
    main()
