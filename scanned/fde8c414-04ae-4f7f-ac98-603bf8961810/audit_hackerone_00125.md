# [M] Buffer Overflow in optimized_escape_html method

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Classic Buffer Overflow
Reporter: chamal
State: resolved
Disclosed: 2022-01-22T14:03:33.908Z
CVE: CVE-2021-41816
Source: https://hackerone.com/reports/1455248

## Details
* This report is a copy of bug report (https://hackerone.com/reports/1328463).
     I was asked to submit this bug here, because Ruby bug bounty program is moved to this new Internet Bug Bounty program.

Operating System
================
Windows 10
*This should reproduce in any other operating system where `long` data type takes 4 bytes.*

Description
==========

This bug is present in `optimized_escape_html` method of [ext\cgi\escape\escape.c](https://github.com/ruby/ruby/blob/master/ext/cgi/escape/escape.c) file.
Below mentioned line causes this bug.
```cpp
char *buf = ALLOCV_N(char, vbuf, RSTRING_LEN(str) * HTML_ESCAPE_MAX_LEN);
```

`RSTRING_LEN` is a preprocessor directive. It expands to below code.
```cpp
static inline long
RSTRING_LEN(VALUE str)
{
    return rbimpl_rstring_getmem(str).as.heap.len;
}
```
`HTML_ESCAPE_MAX_LEN` is defined as this.
``` cpp
#define HTML_ESCAPE_MAX_LEN 6
```
 

Note that `RSTRING_LEN` returns a `long` data type value.
`Long` data type takes 4 bytes on Windows operating system.
So maximum value for a unsigned `long` data type is 4,294,967,295.

Attached test case passes a string, which has 715828054 characters to `CGI.escapeHTML` method.
Length of the buffer is calculated as -> `RSTRING_LEN(str) * HTML_ESCAPE_MAX_LEN`
                                                                                            715828054 * 6 = 4,294,968,324

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1455248_
