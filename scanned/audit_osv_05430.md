# [H] Inefficient Algorithmic Complexity in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-11828
Aliases: CVE-2024-11828
Ecosystem: Bitnami
Published: 2024-11-28
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-11828
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.6.0 <17.6.1

## Details
A denial of service (DoS) condition was discovered in GitLab CE/EE affecting all versions from 13.2.4 before 17.4.5, 17.5 before 17.5.3, and 17.6 before 17.6.1. By leveraging this vulnerability an attacker could create a DoS condition by sending crafted API calls. This was a regression of an earlier patch.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/443559
- https://hackerone.com/reports/2380264
- https://nvd.nist.gov/vuln/detail/CVE-2024-11828
