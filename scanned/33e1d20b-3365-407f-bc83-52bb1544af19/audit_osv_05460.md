# [M] Improper Protection of Alternate Path in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-8311
Aliases: CVE-2024-8311
Ecosystem: Bitnami
Published: 2024-09-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-8311
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.3.0 <17.3.2

## Details
An issue was discovered with pipeline execution policies in GitLab EE affecting all versions from 17.2 prior to 17.2.5, 17.3 prior to 17.3.2 which allows authenticated users to bypass variable overwrite protection via inclusion of a CI/CD template.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/479315
- https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-8311
