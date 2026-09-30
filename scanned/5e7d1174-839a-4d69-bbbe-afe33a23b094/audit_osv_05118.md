# [M] BIT-gitlab-2021-39897

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39897
Aliases: CVE-2021-39897
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39897
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.0.0 <13.0.1

## Details
Improper access control in GitLab CE/EE version 10.5 and above allowed subgroup members with inherited access to a project from a parent group to still have access even after the subgroup is transferred

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39897.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/341017
- https://hackerone.com/reports/1330806
- https://nvd.nist.gov/vuln/detail/CVE-2021-39897
