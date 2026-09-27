# [H] CVE-2021-44481

## Summary
Severity: High
Advisory: CVE-2021-44481
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-04-15
Source: https://osv.dev/vulnerability/CVE-2021-44481
Type: osv

## Details
An issue was discovered in YottaDB through r1.32 and V7.0-000. A lack of parameter validation in calls to memcpy in check_and_set_timeout in sr_unix/ztimeoutroutines.c allows attackers to attempt to read from a NULL pointer.

## References
- https://gitlab.com/YottaDB/DB/YDB/-/issues/828
