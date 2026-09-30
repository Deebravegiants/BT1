# [M] BIT-gitlab-2022-0489

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0489
Aliases: CVE-2022-0489
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0489
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.8.0 <14.8.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting with 8.15 . It was possible to trigger a DOS by using the math feature with a specific formula in issue comments.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0489.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/341832
- https://hackerone.com/reports/1350793
- https://nvd.nist.gov/vuln/detail/CVE-2022-0489
