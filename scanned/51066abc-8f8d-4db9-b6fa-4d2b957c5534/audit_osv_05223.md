# [M] BIT-gitlab-2022-2095

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2095
Aliases: CVE-2022-2095
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2095
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
An improper access control check in GitLab CE/EE affecting all versions starting from 13.7 before 15.0.5, all versions starting from 15.1 before 15.1.4, all versions starting from 15.2 before 15.2.1 allows a malicious authenticated user to view a public project's Deploy Key's public fingerprint and name when that key has write permission. Note that GitLab never asks for nor stores the private key.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2095.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/365415
- https://hackerone.com/reports/1600325
- https://nvd.nist.gov/vuln/detail/CVE-2022-2095
