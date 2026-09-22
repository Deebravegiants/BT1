# [M] BIT-gitlab-2022-2417

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2417
Aliases: CVE-2022-2417
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2417
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.2.0 <15.2.1

## Details
Insufficient validation in GitLab CE/EE affecting all versions from 12.10 prior to 15.0.5, 15.1 prior to 15.1.4, and 15.2 prior to 15.2.1 allows an authenticated and authorised user to import a project that includes branch names which are 40 hexadecimal characters, which could be abused in supply chain attacks where a victim pinned to a specific Git commit of the project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2417.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/361179
- https://nvd.nist.gov/vuln/detail/CVE-2022-2417
