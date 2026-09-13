# [M] CVE-2020-19005

## Summary
Severity: Medium
Advisory: CVE-2020-19005
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-08-25
Source: https://osv.dev/vulnerability/CVE-2020-19005
Type: osv

## Details
zrlog v2.1.0 has a vulnerability with the permission check. If admin account is logged in, other unauthorized users can download the database backup file directly.

## References
- https://github.com/94fzb/zrlog/issues/48
- https://github.com/94fzb/zrlog/commit/b2b4415e2e59b6f18b0a62b633e71c96d63c43ba
