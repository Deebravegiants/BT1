# [M] BIT-gitlab-2020-13297

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13297
Aliases: CVE-2020-13297
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13297
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. When 2 factor authentication was enabled for groups, a malicious user could bypass that restriction by sending a specific query to the API endpoint.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13297.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/32215
- https://hackerone.com/reports/691592
- https://nvd.nist.gov/vuln/detail/CVE-2020-13297
