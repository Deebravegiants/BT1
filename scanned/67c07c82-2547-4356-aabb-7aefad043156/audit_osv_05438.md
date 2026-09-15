# [M] Authentication Bypass by Spoofing in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-1347
Aliases: CVE-2024-1347
Ecosystem: Bitnami
Published: 2024-04-27
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1347
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.11.0 <16.11.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions before 16.9.6, all versions starting from 16.10 before 16.10.4, all versions starting from 16.11 before 16.11.1. Under certain conditions, an attacker through a crafted email address may be able to bypass domain based restrictions on an instance or a group.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/441093
- https://hackerone.com/reports/2355565
- https://nvd.nist.gov/vuln/detail/CVE-2024-1347
