# [M] BIT-gitlab-2022-0390

## Summary
Severity: Medium
Advisory: BIT-gitlab-2022-0390
Aliases: CVE-2022-0390
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2022-0390
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.7.0 <14.7.1

## Details
Improper access control in Gitlab CE/EE versions 12.7 to 14.5.4, 14.6 to 14.6.4, and 14.7 to 14.7.1 allowed for project non-members to retrieve issue details when it was linked to an item from the vulnerability dashboard.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-0390.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/330030
- https://hackerone.com/reports/1179733
- https://nvd.nist.gov/vuln/detail/CVE-2022-0390
