# [M] sprintf combined format string attack

## Summary
Severity: Medium
Program: Ruby
Weakness: Memory Corruption - Generic
Reporter: aerodudrizzt
State: resolved
Disclosed: 2017-09-22T00:05:00.297Z
CVE: CVE-2017-0898
Source: https://hackerone.com/reports/212241

## Details
In a ticket that was also reported to "shopify-scripts" regarding "MRuby", I reported in details a combined attack against the sprintf gem:
* Information leak
* Heap buffer underflow

The full ticket details can be found in:
* Ticket #212239
* The ticked was opened several minutes ago (but I add it in case it will be handled fast enough to be available to you too), and here are the details:

This ticket is somehow connected to Ticket #211190, that suggested another fix to the ```CHECK(l)``` macro. The attached code assumed that the ticket will be fixed like it was fixed in MRuby, however the vulnerabilities apply even without the fix, that was aimed at another vulnerability.

Technical Error 1:
==============
The ```CHECK(l)``` macro can sometimes receive negative values, that will bypass the size checks, since the resize loop is:
```cpp
#define CHECK(l) do {\
/*  int cr = ENC_CODERANGE(result);*/\
  while ((l) >= bsiz - blen) {\
    bsiz*=2;\
  }\
  mrb_str_resize(mrb, result, bsiz);\
/*  ENC_CODERANGE_SET(result, cr);*/\
  buf = RSTRING_PTR(result);\
} while (0)
```
One example for reaching a negative "l" value is in the "G" format when the width is "2 ** 31 - 20", causing need to be ```MIN_INT```:
```cpp
        if ((flags&FWIDTH) && need < width)
            need = width;
        need += 20;

        CHECK(need);
        n = snprintf(&buf[blen], need, fbuf, fval);
        blen += n;
```
Proposed Fix:
--------------------
Since there are several such IOFs, the best fix will be a robust check inside the macro itself.
The macro should add another check to raise an exception in case ```l < 0```.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/212241_
