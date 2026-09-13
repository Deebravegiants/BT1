# [M] BIT-gitlab-2020-13346

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13346
Aliases: CVE-2020-13346
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13346
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
Membership changes are not reflected in ToDo subscriptions in GitLab versions prior to 13.2.10, 13.3.7 and 13.4.2, allowing guest users to access confidential issues through API.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13346.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/219496
- https://hackerone.com/reports/880863
- https://nvd.nist.gov/vuln/detail/CVE-2020-13346
