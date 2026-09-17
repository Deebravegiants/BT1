# [M] BIT-gitlab-2022-4335

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4335
Aliases: CVE-2022-4335
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4335
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
A blind SSRF vulnerability was identified in all versions of GitLab EE prior to 15.4.6, 15.5 prior to 15.5.5, and 15.6 prior to 15.6.1 which allows an attacker to connect to a local host.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4335.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/353018
- https://hackerone.com/reports/1462437
- https://nvd.nist.gov/vuln/detail/CVE-2022-4335
