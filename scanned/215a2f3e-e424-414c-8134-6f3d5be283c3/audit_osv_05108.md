# [M] BIT-gitlab-2021-39886

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39886
Aliases: CVE-2021-39886
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39886
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
Permissions rules were not applied while issues were moved between projects of the same group in GitLab versions starting with 10.6 and up to 14.1.7 allowing users to read confidential Epic references.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39886.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/330520
- https://nvd.nist.gov/vuln/detail/CVE-2021-39886
