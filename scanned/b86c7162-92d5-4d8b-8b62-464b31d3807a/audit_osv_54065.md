# [M] CVE-2023-37770

## Summary
Severity: Medium
Advisory: CVE-2023-37770
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-17
Source: https://osv.dev/vulnerability/CVE-2023-37770
Type: osv

## Details
faust commit ee39a19 was discovered to contain a stack overflow via the component boxppShared::print() at /boxes/ppbox.cpp.

## References
- https://github.com/grame-cncm/faust/issues/922
