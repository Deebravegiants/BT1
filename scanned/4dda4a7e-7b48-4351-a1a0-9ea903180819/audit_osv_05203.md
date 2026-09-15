# [M] BIT-gitlab-2022-1416

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-1416
Aliases: CVE-2022-1416
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-1416
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.10.0 <14.10.1

## Details
Missing sanitization of data in Pipeline error messages in GitLab CE/EE affecting all versions starting from 1.0.2 before 14.8.6, all versions from 14.9.0 before 14.9.4, and all versions from 14.10.0 before 14.10.1 allows for rendering of attacker controlled HTML tags and CSS styling

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1416.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/342988
- https://hackerone.com/reports/1362405
- https://nvd.nist.gov/vuln/detail/CVE-2022-1416
