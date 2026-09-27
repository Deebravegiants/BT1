# [M] BIT-gitlab-2021-39912

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39912
Aliases: CVE-2021-39912
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39912
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
A potential DoS vulnerability was discovered in GitLab CE/EE starting with version 13.7. Using a malformed TIFF images was possible to trigger memory exhaustion.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39912.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/341363
- https://hackerone.com/reports/1330882
- https://nvd.nist.gov/vuln/detail/CVE-2021-39912
