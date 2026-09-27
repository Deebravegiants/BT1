# [H] BIT-gitlab-2020-13303

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13303
Aliases: CVE-2020-13303
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13303
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. Due to improper verification of permissions, an unauthorized user can access a private repository within a public project.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13303.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/238887
- https://hackerone.com/reports/962231
- https://nvd.nist.gov/vuln/detail/CVE-2020-13303
