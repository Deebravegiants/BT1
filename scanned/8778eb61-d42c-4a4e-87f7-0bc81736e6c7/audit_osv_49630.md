# [M] CVE-2019-14872

## Summary
Severity: Medium
Advisory: CVE-2019-14872
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-19
Source: https://osv.dev/vulnerability/CVE-2019-14872
Type: osv

## Details
The _dtoa_r function of the newlib libc library, prior to version 3.3.0, performs multiple memory allocations without checking their return value. This could result in NULL pointer dereference.

## References
- https://census-labs.com/news/2020/01/31/multiple-null-pointer-dereference-vulnerabilities-in-newlib/
