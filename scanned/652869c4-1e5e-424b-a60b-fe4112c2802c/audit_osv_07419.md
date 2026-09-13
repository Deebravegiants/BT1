# [M] BIT-redmine-2020-36308

## Summary
Severity: Medium
Advisory: BIT-redmine-2020-36308
Aliases: CVE-2020-36308
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2020-36308
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.1.0 <4.1.1

## Details
Redmine before 4.0.7 and 4.1.x before 4.1.1 allows attackers to discover the subject of a non-visible issue by performing a CSV export and reading time entries.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2020-36308
