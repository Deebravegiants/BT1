# [M] BIT-gitlab-2021-22196

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22196
Aliases: CVE-2021-22196
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22196
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.10.0 <13.10.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 13.4. It was possible to exploit a stored cross-site-scripting in merge request via a specifically crafted branch name.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22196.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/254710
- https://hackerone.com/reports/977697
- https://nvd.nist.gov/vuln/detail/CVE-2021-22196
