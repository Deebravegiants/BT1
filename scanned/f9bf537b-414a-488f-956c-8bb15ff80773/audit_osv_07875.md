# [M] double free in curl_maprintf

## Summary
Severity: Medium
Advisory: CURL-CVE-2016-8618
Aliases: CVE-2016-8618
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CURL-CVE-2016-8618
Type: osv

## Details
The libcurl API function called `curl_maprintf()` can be tricked into doing a
double free due to an unsafe `size_t` multiplication, on systems using 32-bit
`size_t` variables. The function is also used internally in numerous
situations.

The function doubles an allocated memory area with realloc() and allows the
size to wrap and become zero and when doing so realloc() returns NULL *and*
frees the memory - in contrary to normal realloc() fails where it only returns
NULL - causing libcurl to free the memory *again* in the error path.

Systems with 64-bit versions of the `size_t` type are not affected by this
issue.

This behavior can be triggered using the publicly exposed function.
