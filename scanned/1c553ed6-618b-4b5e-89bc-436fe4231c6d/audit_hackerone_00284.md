# [C] Exim use-after-free vulnerability while reading mail header involving BDAT commands

## Summary
Severity: Critical (CVSS 9.8)
Program: Internet Bug Bounty
Weakness: Use After Free
Reporter: mehqq
State: resolved
Disclosed: 2019-11-12T23:45:11.583Z
CVE: CVE-2017-16943
Source: https://hackerone.com/reports/296991

## Details
Original article is [here](https://devco.re/blog/2017/12/11/Exim-RCE-advisory-CVE-2017-16943-en/)

# Use-after-free in receive_msg leads to RCE

### Vulnerability Analysis
To explain this bug, we need to start with the memory management of exim. There is a series of functions starts with `store_` such as `store_get`, `store_release`, `store_reset`. These functions are used to manage dynamically allocated memory and improve performance. Its architecture is like the illustration below:
![architecture of storeblock](https://d2mxuefqeaa7sj.cloudfront.net/s_250CBD95095D0019FAC82FED4F605A7EFB015920E271206EB018526E9DD7E3F0_1510286247190_exim+store+1.png)

Initially, exim allocates a big storeblock (default 0x2000) and then cut it into **stores** when `store_get` is called, using global pointers to record the size of unused memory and where to cut in next allocation. Once the `current_block` is insufficient, it allocates a new block and appends it to the end of the chain, which is a linked list, and then makes `current_block` point to it. Exim maintains three `store_pool`, that is, there are three chains like the illustration above and every global variables are actually arrays.
This vulnerability is in `receive_msg` where exim reads headers: 
[receive.c: 1817 receive_msg](https://github.com/Exim/exim/blob/e924c08b7d031b712013a7a897e2d430b302fe6c/src/src/receive.c#L1817)
```c
  if (ptr >= header_size - 4)
    {
    int oldsize = header_size;
    /* header_size += 256; */
    header_size *= 2;
    if (!store_extend(next->text, oldsize, header_size))
      {
      uschar *newtext = store_get(header_size);
      memcpy(newtext, next->text, ptr);
      store_release(next->text);
      next->text = newtext;
      }
    }
```
It seems normal if the store functions are just like realloc, malloc and free. However, they are different and cannot be used in this way. When exim tries to **extend** store, the function `store_extend` checks whether the old store is the latest store allocated in `current_block`. It returns False immediately if the check is failed.
[store.c: 276 store_extend](https://github.com/Exim/exim/blob/e924c08b7d031b712013a7a897e2d430b302fe6c/src/src/store.c#L276)
```c
if (CS ptr + rounded_oldsize != CS (next_yield[store_pool]) ||
    inc > yield_length[store_pool] + rounded_oldsize - oldsize)
  return FALSE;
```
Once `store_extend` fails, exim tries to get a new store and release the old one. After we look into  `store_get` and store_release, we found that `store_get` returns a **store**, but `store_release` releases a **block** if the store is at the head of it. That is to say, if `next->text` points to the start the `current_block` and `store_get` cuts store inside it for `newtext`, then `store_release(next->text)` frees `next->text`, which is equal to `current_block`, and leaves `newtext` and `current_block` pointing to a freed memory area. Any further usage of these pointers leads to a use-after-free vulnerability. To trigger this bug, we need to make exim call `store_get` after `next->text` is allocated. This was impossible until BDAT command was introduced into exim. BDAT makes `store_get` reachable and finally leads to an RCE.
Exim uses [function pointers](https://github.com/Exim/exim/blob/e924c08b7d031b712013a7a897e2d430b302fe6c/src/src/globals.h#L136) to switch between different input sources, such as `receive_getc`, `receive_getbuf`. When receiving BDAT data, `receive_getc` is set to `bdat_getc` in order to check left chunking data size and to handle following command of BDAT. In `receive_msg`, exim also uses `receive_getc`. It loops to read data, and stores data into `next->text`, extends if insufficient.
[receive.c: 1817 receive_msg](https://github.com/Exim/exim/blob/e924c08b7d031b712013a7a897e2d430b302fe6c/src/src/receive.c#L1789)
```c
for (;;)
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/296991_
