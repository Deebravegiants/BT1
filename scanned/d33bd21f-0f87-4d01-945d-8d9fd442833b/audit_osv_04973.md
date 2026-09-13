# [H] BIT-gitlab-2020-13334

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13334
Aliases: CVE-2020-13334
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13334
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
In GitLab versions prior to 13.2.10, 13.3.7 and 13.4.2, improper authorization checks allow a non-member of a project/group to change the confidentiality attribute of issue via mutation GraphQL query

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13334.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/195327
- https://hackerone.com/reports/762271
- https://nvd.nist.gov/vuln/detail/CVE-2020-13334
