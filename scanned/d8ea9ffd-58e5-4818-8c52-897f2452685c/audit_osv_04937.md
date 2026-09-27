# [M] BIT-gitlab-2020-13294

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13294
Aliases: CVE-2020-13294
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13294
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.2.0 <13.2.3

## Details
In GitLab before 13.0.12, 13.1.6 and 13.2.3, access grants were not revoked when a user revoked access to an application.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13294.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/26147
- https://hackerone.com/reports/469728
- https://nvd.nist.gov/vuln/detail/CVE-2020-13294
