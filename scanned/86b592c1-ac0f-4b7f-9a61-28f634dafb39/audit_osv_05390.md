# [H] Incorrect Execution-Assigned Permissions in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-3915
Aliases: CVE-2023-3915
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-3915
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.3.0 <16.3.1

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 16.1 before 16.1.5, all versions starting from 16.2 before 16.2.5, all versions starting from 16.3 before 16.3.1. If an external user is given an owner role on any group, that external user may escalate their privileges on the instance by creating a service account in that group. This service account is not classified as external and may be used to access internal projects.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/417664
- https://hackerone.com/reports/2040834
- https://nvd.nist.gov/vuln/detail/CVE-2023-3915
