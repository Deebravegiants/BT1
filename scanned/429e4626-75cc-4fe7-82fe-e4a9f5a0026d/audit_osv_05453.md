# [M] Incorrect Provision of Specified Functionality in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-5005
Aliases: CVE-2024-5005
Ecosystem: Bitnami
Published: 2024-10-15
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-5005
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.4.0 <17.4.2

## Details
An issue has been discovered discovered in GitLab EE/CE affecting all versions starting from 11.4 before 17.2.9, all versions starting from 17.3 before 17.3.5, all versions starting from 17.4 before 17.4.2 It was possible for guest users to disclose project templates using the API.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/462108
- https://hackerone.com/reports/2501461
- https://nvd.nist.gov/vuln/detail/CVE-2024-5005
