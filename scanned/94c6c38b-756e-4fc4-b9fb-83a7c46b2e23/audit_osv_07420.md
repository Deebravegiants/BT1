# [H] BIT-redmine-2021-30163

## Summary
Severity: High
Advisory: BIT-redmine-2021-30163
Aliases: CVE-2021-30163
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-30163
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.1.0 <4.1.2

## Details
Redmine before 4.0.8 and 4.1.x before 4.1.2 allows attackers to discover the names of private projects if issue-journal details exist that have changes to project_id values.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-30163
