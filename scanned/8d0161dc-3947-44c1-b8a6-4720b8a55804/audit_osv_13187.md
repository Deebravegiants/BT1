# [M] CVE-2018-18481

## Summary
Severity: Medium
Advisory: CVE-2018-18481
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-18481
Type: osv

## Details
A heap-based buffer over-read exists in libopencad 0.2.0 in the ReadCHAR function in lib/dwg/io.cpp, resulting in an application crash.

## References
- https://github.com/sandyre/libopencad/issues/43
