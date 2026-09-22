# [H] BIT-redmine-2021-31863

## Summary
Severity: High
Advisory: BIT-redmine-2021-31863
Aliases: CVE-2021-31863
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-31863
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.2.0 <4.2.1

## Details
Insufficient input validation in the Git repository integration of Redmine before 4.0.9, 4.1.x before 4.1.3, and 4.2.x before 4.2.1 allows Redmine users to read arbitrary local files accessible by the application server process.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/news/131
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-31863
