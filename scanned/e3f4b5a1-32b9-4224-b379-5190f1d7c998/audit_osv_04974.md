# [M] BIT-gitlab-2020-13335

## Summary
Severity: Medium
Advisory: BIT-gitlab-2020-13335
Aliases: CVE-2020-13335
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13335
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.4.0 <13.4.2

## Details
Improper group membership validation when deleting a user account in GitLab >=7.12 allows a user to delete own account without deleting/transferring their group.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13335.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/27231
- https://hackerone.com/reports/503823
- https://nvd.nist.gov/vuln/detail/CVE-2020-13335
