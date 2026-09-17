# [H] BIT-gitlab-2022-4331

## Summary
Severity: High
Advisory: BIT-gitlab-2022-4331
Aliases: CVE-2022-4331
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-4331
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=15.9.0 <15.9.2

## Details
An issue has been discovered in GitLab EE affecting all versions starting from 15.1 before 15.7.8, all versions starting from 15.8 before 15.8.4, all versions starting from 15.9 before 15.9.2. If a group with SAML SSO enabled is transferred to a new namespace as a child group, it's possible previously removed malicious maintainer or owner of the child group can still gain access to the group via SSO or a SCIM token to perform actions on the group.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-4331.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/385050
- https://hackerone.com/reports/1791518
- https://nvd.nist.gov/vuln/detail/CVE-2022-4331
