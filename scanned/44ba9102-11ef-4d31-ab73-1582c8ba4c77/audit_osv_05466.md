# [C] Missing Authentication for Critical Function in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2024-9164
Aliases: CVE-2024-9164
Ecosystem: Bitnami
Published: 2024-10-15
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-9164
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.2

## Details
An issue was discovered in GitLab EE affecting all versions starting from 12.5 prior to 17.2.9, starting from 17.3, prior to 17.3.5, and starting from 17.4 prior to 17.4.2, which allows running pipelines on arbitrary branches.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/493946
- https://hackerone.com/reports/2711204
- https://nvd.nist.gov/vuln/detail/CVE-2024-9164
