# [M] BIT-gitlab-2021-39907

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39907
Aliases: CVE-2021-39907
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39907
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
A potential DOS vulnerability was discovered in GitLab CE/EE starting with version 13.7. The stripping of EXIF data from certain images resulted in high CPU usage.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39907.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/299869
- https://hackerone.com/reports/1083182
- https://nvd.nist.gov/vuln/detail/CVE-2021-39907
