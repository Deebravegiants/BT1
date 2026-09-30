# [M] BIT-gitlab-2022-3740

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-3740
Aliases: CVE-2022-3740
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-3740
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.6.0 <15.6.1

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 12.9 prior to 15.3.5, 15.4 prior to 15.4.4, and 15.5 prior to 15.5.2. A group owner may be able to bypass External Authorization check, if it is enabled, to access git repositories and package registries by using Deploy tokens or Deploy keys .

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-3740.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/368416
- https://hackerone.com/reports/1602904
- https://nvd.nist.gov/vuln/detail/CVE-2022-3740
