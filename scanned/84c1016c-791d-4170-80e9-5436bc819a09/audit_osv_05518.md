# [M] Insufficiently Protected Credentials in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2026-11827
Aliases: CVE-2026-11827
Ecosystem: Bitnami
Published: 2026-07-13
Source: https://osv.dev/vulnerability/BIT-gitlab-2026-11827
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=19.1.0 <19.1.2

## Details
GitLab has remediated an issue in GitLab EE affecting all versions from 9.5 before 18.11.7, 19.0 before 19.0.4, and 19.1 before 19.1.2 that under certain conditions could have allowed an authenticated user with maintainer-role permissions to obtain another user's stored credentials due to improper authorization controls.

## References
- https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-1-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/work_items/602478
- https://hackerone.com/reports/3720483
- https://nvd.nist.gov/vuln/detail/CVE-2026-11827
