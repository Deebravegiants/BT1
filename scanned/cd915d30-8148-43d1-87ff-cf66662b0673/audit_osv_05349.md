# [M] URL Redirection to Untrusted Site in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-1279
Aliases: CVE-2023-1279
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-1279
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab affecting all versions starting from 4.1 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1 where it was possible to create a URL that would redirect to a different project.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/395437
- https://hackerone.com/reports/1889230
- https://nvd.nist.gov/vuln/detail/CVE-2023-1279
