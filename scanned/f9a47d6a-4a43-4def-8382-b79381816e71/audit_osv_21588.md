# [H] CVE-2021-44483

## Summary
Severity: High
Advisory: CVE-2021-44483
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44483
Type: osv

## Details
An issue was discovered in YottaDB through r1.32 and V7.0-000. A lack of input validation in calls to eb_div in sr_port/eb_muldiv.c allows attackers to crash the application by performing a divide by zero.

## References
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
