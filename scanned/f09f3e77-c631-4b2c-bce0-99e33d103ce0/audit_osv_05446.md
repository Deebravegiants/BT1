# [M] Improper Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-3959
Aliases: CVE-2024-3959
Ecosystem: Bitnami
Published: 2024-06-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-3959
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.1.0 <17.1.1

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 16.7 prior to 16.11.5, starting from 17.0 prior to 17.0.3, and starting from 17.1 prior to 17.1.1, which allows private job artifacts can be accessed by any user.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/456989
- https://hackerone.com/reports/2456845
- https://nvd.nist.gov/vuln/detail/CVE-2024-3959
