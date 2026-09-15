# [H] BIT-gitlab-2020-13356

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13356
Aliases: CVE-2020-13356
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13356
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=0 <13.5.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 8.8.9. A specially crafted request could bypass Multipart protection and read files in certain specific paths on the server. Affected versions are: >=8.8.9, <13.3.9,>=13.4, <13.4.5,>=13.5, <13.5.2.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13356.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/230878
- https://hackerone.com/reports/927953
- https://nvd.nist.gov/vuln/detail/CVE-2020-13356
