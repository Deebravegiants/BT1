# [H] Inefficient Regular Expression Complexity in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2023-0632
Aliases: CVE-2023-0632
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-0632
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.2.0 <16.2.2

## Details
An issue has been discovered in GitLab affecting all versions starting from 15.2 before 16.0.8, all versions starting from 16.1 before 16.1.3, all versions starting from 16.2 before 16.2.2. A Regular Expression Denial of Service was possible by using crafted payloads to search Harbor Registry.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/390148
- https://hackerone.com/reports/1852677
- https://nvd.nist.gov/vuln/detail/CVE-2023-0632
