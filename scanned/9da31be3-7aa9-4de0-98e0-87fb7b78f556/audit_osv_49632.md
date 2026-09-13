# [M] CVE-2019-14874

## Summary
Severity: Medium
Advisory: CVE-2019-14874
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-19
Source: https://osv.dev/vulnerability/CVE-2019-14874
Type: osv

## Details
In the __i2b function of the newlib libc library, all versions prior to 3.3.0 (see newlib/libc/stdlib/mprec.c), Balloc is used to allocate a big integer, however no check is performed to verify if the allocation succeeded or not. The access of _ x[0] will trigger a null pointer dereference bug in case of a memory allocation failure.

## References
- https://census-labs.com/news/2020/01/31/multiple-null-pointer-dereference-vulnerabilities-in-newlib/
