# [C] Missing Authorization in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2025-5121
Aliases: CVE-2025-5121
Ecosystem: Bitnami
Published: 2025-06-24
Source: https://osv.dev/vulnerability/BIT-gitlab-2025-5121
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.11.0 <18.0.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions from 17.11 before 17.11.4 and 18.0 before 18.0.2. A missing authorization check may have allowed compliance frameworks to be applied to projects outside the compliance framework's group.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/545429
- https://hackerone.com/reports/3153908
- https://nvd.nist.gov/vuln/detail/CVE-2025-5121
