# [C] BIT-redmine-2021-30164

## Summary
Severity: Critical
Advisory: BIT-redmine-2021-30164
Aliases: CVE-2021-30164
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-30164
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.1.0 <4.1.2

## Details
Redmine before 4.0.8 and 4.1.x before 4.1.2 allows attackers to bypass the add_issue_notes permission requirement by leveraging the Issues API.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-30164
