# [H] CVE-2020-35342

## Summary
Severity: High
Advisory: CVE-2020-35342
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-35342
Type: osv

## Details
GNU Binutils before 2.34 has an uninitialized-heap vulnerability in function tic4x_print_cond (file opcodes/tic4x-dis.c) which could allow attackers to make an information leak.

## References
- https://security.netapp.com/advisory/ntap-20231006-0009/
- https://sourceware.org/bugzilla/show_bug.cgi?id=25319
