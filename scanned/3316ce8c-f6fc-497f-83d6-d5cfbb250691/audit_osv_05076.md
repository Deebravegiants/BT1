# [M] BIT-gitlab-2021-22248

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22248
Aliases: CVE-2021-22248
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22248
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.1.0 <14.1.2

## Details
Improper authorization on the pipelines page in GitLab CE/EE affecting all versions since 13.12 allowed unauthorized users to view some pipeline information for public projects that have access to pipelines restricted to members only

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22248.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/336074
- https://nvd.nist.gov/vuln/detail/CVE-2021-22248
