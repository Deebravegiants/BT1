# [H] CVE-2021-44490

## Summary
Severity: High
Advisory: CVE-2021-44490
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44490
Type: osv

## Details
An issue was discovered in YottaDB through r1.32 and V7.0-000. Using crafted input, attackers can cause a calculation of the size of calls to memset in op_fnj3 in sr_port/op_fnj3.c to result in an extremely large value in order to cause a segmentation fault and crash the application. This is a "- (digs < 1 ? 1 : digs)" subtraction.

## References
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
