# [M] Uncontrolled Resource Consumption in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-1493
Aliases: CVE-2024-1493
Ecosystem: Bitnami
Published: 2024-06-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1493
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.1.0 <17.1.1

## Details
An issue was discovered in GitLab CE/EE affecting all versions starting from 9.2 prior to 16.11.5, starting from 17.0 prior to 17.0.3, and starting from 17.1 prior to 17.1.1, with the processing logic for generating link in dependency files can lead to a regular  expression DoS attack on the server

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/441806
- https://hackerone.com/reports/2370084
- https://nvd.nist.gov/vuln/detail/CVE-2024-1493
