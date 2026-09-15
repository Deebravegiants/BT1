# [M] BIT-redmine-2021-31866

## Summary
Severity: Medium
Advisory: BIT-redmine-2021-31866
Aliases: CVE-2021-31866
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-redmine-2021-31866
Type: osv

## Affected
- Bitnami: `redmine` — affected >=4.1.0 <4.1.3

## Details
Redmine before 4.0.9 and 4.1.x before 4.1.3 allows an attacker to learn the values of internal authentication keys by observing timing differences in string comparison operations within SysController and MailHandlerController.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00013.html
- https://www.redmine.org/news/131
- https://www.redmine.org/projects/redmine/wiki/Security_Advisories
- https://nvd.nist.gov/vuln/detail/CVE-2021-31866
