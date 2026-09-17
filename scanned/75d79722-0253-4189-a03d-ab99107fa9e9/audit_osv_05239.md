# [M] BIT-gitlab-2022-2455

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2455
Aliases: CVE-2022-2455
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2455
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
A business logic issue in the handling of large repositories in all versions of GitLab CE/EE from 10.0 before 15.1.6, all versions starting from 15.2 before 15.2.4, all versions starting from 15.3 before 15.3.2 allowed an authenticated and authorized user to exhaust server resources by importing a malicious project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2455.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/359964
- https://hackerone.com/reports/1542230
- https://nvd.nist.gov/vuln/detail/CVE-2022-2455
