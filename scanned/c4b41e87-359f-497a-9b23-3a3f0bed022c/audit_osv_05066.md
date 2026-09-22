# [H] BIT-gitlab-2021-22236

## Summary
Severity: High
Advisory: BIT-gitlab-2021-22236
Aliases: CVE-2021-22236
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22236
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
Due to improper handling of OAuth client IDs, new subscriptions generated OAuth tokens on an incorrect OAuth client application. This vulnerability is present in GitLab CE/EE since version 14.1.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22236.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/334925
- https://nvd.nist.gov/vuln/detail/CVE-2021-22236
