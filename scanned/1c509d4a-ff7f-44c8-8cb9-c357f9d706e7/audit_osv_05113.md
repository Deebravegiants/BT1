# [M] BIT-gitlab-2021-39891

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39891
Aliases: CVE-2021-39891
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39891
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE since version 8.0, access tokens created as part of admin's impersonation of a user are not cleared at the end of impersonation which may lead to unnecessary sensitive info disclosure.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39891.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/335137
- https://nvd.nist.gov/vuln/detail/CVE-2021-39891
