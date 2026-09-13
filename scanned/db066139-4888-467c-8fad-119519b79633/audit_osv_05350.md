# [M] Insertion of Sensitive Information Into Sent Data in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1401
Aliases: CVE-2023-1401
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1401
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=3.0.29 <4.0.5

## Details
An issue has been discovered in GitLab DAST scanner affecting all versions starting from 3.0.29 before 4.0.5, in which the DAST scanner leak cross site cookies on redirect during authorization.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/396533
- https://hackerone.com/reports/1889255
- https://nvd.nist.gov/vuln/detail/CVE-2023-1401
