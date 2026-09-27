# [M] BIT-gitlab-2021-22172

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22172
Aliases: CVE-2021-22172
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22172
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.8.0 <13.8.2

## Details
Improper authorization in GitLab 12.8+ allows a guest user in a private project to view tag data that should be inaccessible on the releases page

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22172.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/212911
- https://hackerone.com/reports/833334
- https://nvd.nist.gov/vuln/detail/CVE-2021-22172
