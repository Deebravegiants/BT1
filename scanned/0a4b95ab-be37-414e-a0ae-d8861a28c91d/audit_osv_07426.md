# [H] BIT-redmine-2021-37156

## Summary
Severity: High
Advisory: BIT-redmine-2021-37156
Aliases: CVE-2021-37156
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-37156
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.2.1 <4.2.2

## Details
Redmine 4.2.0 and 4.2.1 allow existing user sessions to continue upon enabling two-factor authentication for the user's account, but the intended behavior is for those sessions to be terminated.

## References
- https://www.redmine.org/news/132
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-37156
