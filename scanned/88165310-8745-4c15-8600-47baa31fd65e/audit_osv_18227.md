# [C] CVE-2020-25412

## Summary
Severity: Critical
Advisory: CVE-2020-25412
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-25412
Type: osv

## Details
com_line() in command.c in gnuplot 5.4 leads to an out-of-bounds-write from strncpy() that may lead to arbitrary code execution.

## References
- https://sourceforge.net/p/gnuplot/bugs/2303/
