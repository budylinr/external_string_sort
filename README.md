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
