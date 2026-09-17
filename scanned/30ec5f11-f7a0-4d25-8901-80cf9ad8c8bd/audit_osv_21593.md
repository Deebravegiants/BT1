# [C] CVE-2021-44488

## Summary
Severity: Critical
Advisory: CVE-2021-44488
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44488
Type: osv

## Details
An issue was discovered in YottaDB through r1.32 and V7.0-000. Using crafted input, attackers can control the size and input to calls to memcpy in op_fnfnumber in sr_port/op_fnfnumber.c in order to corrupt memory or crash the application.

## References
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
