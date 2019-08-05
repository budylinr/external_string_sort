# external_string_sort
I am solving the following task. I have big file which doesn't fit into memory and I want to sort strings of this file in lexicographical order.

I put some restrictions on this task:
- strings contains only from small english letters
- any string is less then reading chunk size (default chunk size is 16 mb)

I make this via external merge sort. In k-merge phase I use uncompressed trie to sort incoming strings. 

So algorithm is the following:
- split big file into list of files which we sort in memory
- then begin merge phase. During one merge we merge k = M // B sorted files into one file. Here M and B is Vitter notations from External memory model. 
M is some constant proportional to RAM that we use and B is size of read and write buffer.  The actual memory usage in this task can be 2-3 times 
bigger than M (memory for trie). At one time we make number of files k times less, so number of merge levels is log_k(N / M) where N / M is the number
of files after initial sorting.
- in k-merge I use trie to sort. I consequently add chunk of B size from each file to trie and then begin to pop minimal element 
from trie and add following element from the same file to trie. Untill all files will be read and trie is empty. 

It takes 120 seconds to sort file of 150 mb with M = 100mb and B = 16 mb

 What can be done if i have more time:
 - add multiprocessing on IO operations and processing
 - add support for non-english letters (with english letters i can use fast Bitset)
 - make trie compressed. Code suffix w[i:j] with (w, i, j). Problem is to change w on some other u when we pop up
 w because collector can't delete w if there is some reference.
 - make support for very long strings. I suggest to read only B bytes from such strings from the begining. So we have
  truncated version of string. We make sort as usual. And if we have equalities between
 such truncated strings (which is very rare if strings are random) to download next B bytes of each string.