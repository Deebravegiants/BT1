# [M] BIT-gitlab-2022-1417

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1417
Aliases: CVE-2022-1417
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1417
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Improper access control in GitLab CE/EE affecting all versions starting from 8.12 before 14.8.6, all versions starting from 14.9 before 14.9.4, and all versions starting from 14.10 before 14.10.1 allows non-project members to access contents of Project Members-only Wikis via malicious CI jobs

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1417.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/297282
- https://hackerone.com/reports/1075586
- https://nvd.nist.gov/vuln/detail/CVE-2022-1417
