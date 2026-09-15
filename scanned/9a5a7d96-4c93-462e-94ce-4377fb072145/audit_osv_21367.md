# [H] CVE-2021-42523

## Summary
Severity: High
Advisory: CVE-2021-42523
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-42523
Type: osv

## Details
There are two Information Disclosure vulnerabilities in colord, and they lie in colord/src/cd-device-db.c and colord/src/cd-profile-db.c separately. They exist because the 'err_msg' of 'sqlite3_exec' is not releasing after use, while libxml2 emphasizes that the caller needs to release it.

## References
- https://github.com/hughsie/colord/issues/110
