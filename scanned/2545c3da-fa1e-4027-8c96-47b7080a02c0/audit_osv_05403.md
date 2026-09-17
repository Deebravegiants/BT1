# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-4812
Aliases: CVE-2023-4812
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-4812
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.7.0 <16.7.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.3 before 16.5.6, all versions starting from 16.6 before 16.6.4, all versions starting from 16.7 before 16.7.2. The required CODEOWNERS approval could be bypassed by adding changes to a previously approved merge request.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/424398
- https://hackerone.com/reports/2115574
- https://nvd.nist.gov/vuln/detail/CVE-2023-4812
