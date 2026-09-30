# [H] CVE-2018-10528

## Summary
Severity: High
Advisory: CVE-2018-10528
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-04-29
Source: https://osv.dev/vulnerability/CVE-2018-10528
Type: osv

## Details
An issue was discovered in LibRaw 0.18.9. There is a stack-based buffer overflow in the utf2char function in libraw_cxx.cpp.

## References
- https://github.com/LibRaw/LibRaw/issues/144
- https://usn.ubuntu.com/3639-1/
- https://github.com/LibRaw/LibRaw/commit/efd8cfabb93fd0396266a7607069901657c082e3
