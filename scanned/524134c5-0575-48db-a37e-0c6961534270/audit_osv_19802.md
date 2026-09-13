# [H] CVE-2021-25958

## Summary
Severity: High
Advisory: CVE-2021-25958
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-25958
Type: osv

## Details
In Apache Ofbiz, versions v17.12.01 to v17.12.07 implement a try catch exception to handle errors at multiple locations but leaks out sensitive table info which may aid the attacker for further recon. A user can register with a very long password, but when he tries to login with it an exception occurs.

## References
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25958
- https://github.com/apache/ofbiz-framework/commit/2f5b8d33e32c4d9a48243cf9e503236acd5aec5c
