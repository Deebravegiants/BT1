# [C] CVE-2017-7226

## Summary
Severity: Critical
Advisory: CVE-2017-7226
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-03-22
Source: https://osv.dev/vulnerability/CVE-2017-7226
Type: osv

## Details
The pe_ILF_object_p function in the Binary File Descriptor (BFD) library (aka libbfd), as distributed in GNU Binutils 2.28, is vulnerable to a heap-based buffer over-read of size 4049 because it uses the strlen function instead of strnlen, leading to program crashes in several utilities such as addr2line, size, and strings. It could lead to information disclosure as well.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=20905
