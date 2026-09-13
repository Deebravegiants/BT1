# [M] BIT-gitlab-2022-4201

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-4201
Aliases: CVE-2022-4201
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4201
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
A blind SSRF in GitLab CE/EE affecting all from 11.3 prior to 15.4.6, 15.5 prior to 15.5.5, and 15.6 prior to 15.6.1 allows an attacker to connect to local addresses when configuring a malicious GitLab Runner.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4201.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/30376
- https://nvd.nist.gov/vuln/detail/CVE-2022-4201
