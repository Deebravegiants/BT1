# [H] URL Buffer Overflow

## Summary
Severity: High
Advisory: CURL-CVE-2005-4077
Aliases: CVE-2005-4077
Published: 2005-12-07
Source: https://osv.dev/vulnerability/CURL-CVE-2005-4077
Type: osv

## Details
libcurl's URL parser function can overflow a heap based buffer in two ways, if
given a too long URL.

These overflows happen if you

 1 - pass in a URL with no protocol (like "http://") prefix, using no slash
     and the string is 256 bytes or longer. This leads to a single zero byte
     overflow of the heap buffer.

 2 - pass in a URL with only a question mark as separator (no slash) between
     the host and the query part of the URL. This leads to a single zero byte
     overflow of the heap buffer.

Both overflows can be made with the same input string, leading to two single
zero byte overwrites.

The affected flaw cannot be triggered by a redirect, but the long URL must be
passed in "directly" to libcurl. It makes this a "local" problem. Of course,
lots of programs may still pass in user-provided URLs to libcurl without doing
much syntax checking of their own, allowing a user to exploit this
vulnerability.
