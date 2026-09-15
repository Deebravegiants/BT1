# [C] CVE-2021-44486

## Summary
Severity: Critical
Advisory: CVE-2021-44486
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44486
Type: osv

## Details
An issue was discovered in YottaDB through r1.32 and V7.0-000. Using crafted input, attackers can manipulate the value of a function pointer used in op_write in sr_port/op_write.c in order to gain control of the flow of execution.

## References
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
