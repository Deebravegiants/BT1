# [M] BIT-gitlab-2021-22231

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-22231
Aliases: CVE-2021-22231
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-22231
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.0.0 <14.0.2

## Details
A denial of service in user's profile page is found starting with GitLab CE/EE 8.0 that allows attacker to reject access to their profile page via using a specially crafted username.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22231.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/26295
- https://hackerone.com/reports/475098
- https://nvd.nist.gov/vuln/detail/CVE-2021-22231
