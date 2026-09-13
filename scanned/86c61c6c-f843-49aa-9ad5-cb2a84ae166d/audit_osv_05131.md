# [M] BIT-gitlab-2021-39913

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39913
Aliases: CVE-2021-39913
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39913
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.4.0 <14.4.1

## Details
Accidental logging of system root password in the migration log in all versions of GitLab CE/EE before 14.2.6, all versions starting from 14.3 before 14.3.4, and all versions starting from 14.4 before 14.4.1 allows an attacker with local file system access to obtain system root-level privileges

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39913.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/28074
- https://nvd.nist.gov/vuln/detail/CVE-2021-39913
