# [M] Incorrect Authorization in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-6564
Aliases: CVE-2023-6564
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-6564
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.6.1 <16.6.2

## Details
An issue has been discovered in GitLab EE Premium and Ultimate affecting versions 16.4.3, 16.5.3, and 16.6.1. In projects using subgroups to define who can push and/or merge to protected branches, there may have been instances in which subgroup members with the Developer role were able to push or merge to protected branches.

## References
- https://gitlab.com/gitlab-com/gl-infra/production/-/issues/17213
- https://nvd.nist.gov/vuln/detail/CVE-2023-6564
