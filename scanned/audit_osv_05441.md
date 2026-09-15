# [M] Improper Handling of Highly Compressed Data (Data Amplification) in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2024-1947
Aliases: CVE-2024-1947
Ecosystem: Bitnami
Published: 2024-05-29
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-1947
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.0.0 <17.0.1

## Details
A denial of service (DoS) condition was discovered in GitLab CE/EE affecting all versions from 13.2.4 before 16.10.6, 16.11 before 16.11.3, and 17.0 before 17.0.1. By leveraging this vulnerability an attacker could create a DoS condition by sending crafted API calls.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/443559
- https://hackerone.com/reports/2380264
- https://nvd.nist.gov/vuln/detail/CVE-2024-1947
