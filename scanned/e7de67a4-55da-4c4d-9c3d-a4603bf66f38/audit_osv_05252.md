# [M] BIT-gitlab-2022-2592

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-2592
Aliases: CVE-2022-2592
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-2592
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.3.0 <15.3.2

## Details
A lack of length validation in Snippet descriptions in GitLab CE/EE affecting all versions prior to 15.1.6, 15.2 prior to 15.2.4 and 15.3 prior to 15.3.2 allows an authenticated attacker to create a maliciously large Snippet which when requested with or without authentication places excessive load on the server, potential leading to Denial of Service.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-2592.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/362566
- https://hackerone.com/reports/1544507
- https://nvd.nist.gov/vuln/detail/CVE-2022-2592
