# [M] Authentication Bypass by Primary Weakness in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-4784
Aliases: CVE-2024-4784
Ecosystem: Bitnami
Published: 2024-08-10
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-4784
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.2.0 <17.2.2

## Details
An issue was discovered in GitLab EE starting from version 16.7 before 17.0.6, version 17.1 before 17.1.4 and 17.2 before 17.2.2 that allowed bypassing the password re-entry requirement to approve a policy.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/461248
- https://hackerone.com/reports/2486223
- https://nvd.nist.gov/vuln/detail/CVE-2024-4784
