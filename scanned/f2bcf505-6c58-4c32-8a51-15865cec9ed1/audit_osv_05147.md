# [M] BIT-gitlab-2021-39938

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39938
Aliases: CVE-2021-39938
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39938
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.5.0 <14.5.2

## Details
A vulnerable regular expression pattern in GitLab CE/EE since version 8.15 before 14.3.6, all versions starting from 14.4 before 14.4.4, all versions starting from 14.5 before 14.5.2, allows an attacker to cause uncontrolled resource consumption leading to Denial of Service via specially crafted deploy Slash commands

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39938.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/344873
- https://nvd.nist.gov/vuln/detail/CVE-2021-39938
