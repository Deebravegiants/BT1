# [M] BIT-redmine-2021-31864

## Summary
Severity: Medium
Advisory: BIT-redmine-2021-31864
Aliases: CVE-2021-31864
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-31864
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.2.0 <4.2.1

## Details
Redmine before 4.0.9, 4.1.x before 4.1.3, and 4.2.x before 4.2.1 allows attackers to bypass the add_issue_notes permission requirement by leveraging the incoming mail handler.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/news/131
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-31864
