# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-3484
Aliases: CVE-2023-3484
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3484
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.1.0 <16.1.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 12.8 before 15.11.11, all versions starting from 16.0 before 16.0.7, all versions starting from 16.1 before 16.1.2. An attacker could change the name or path of a public top-level group in certain situations.

## References
- https://about.gitlab.com/releases/2023/07/05/security-release-gitlab-16-1-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/416773
- https://hackerone.com/reports/2035687
- https://nvd.nist.gov/vuln/detail/CVE-2023-3484
