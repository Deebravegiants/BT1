# [C] BIT-gitlab-2023-2478

## Summary
Severity: Critical
Advisory: BIT-gitlab-2023-2478
Aliases: CVE-2023-2478
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-2478
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.11.0 <15.11.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.4 before 15.9.7, all versions starting from 15.10 before 15.10.6, all versions starting from 15.11 before 15.11.2. Under certain conditions, a malicious unauthorized GitLab user may use a GraphQL endpoint to attach a malicious runner to any project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2023/CVE-2023-2478.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/409470
- https://hackerone.com/reports/1969599
- https://nvd.nist.gov/vuln/detail/CVE-2023-2478
