# [M] Server-Side Request Forgery (SSRF) in GitLab

## Summary
Severity: Medium
Advisory: BIT-gitlab-2023-6195
Aliases: CVE-2023-6195
Ecosystem: Bitnami
Published: 2025-02-01
Source: https://osv.dev/vulnerability/BIT-gitlab-2023-6195
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.11.0 <16.11.2

## Details
An issue has been discovered in GitLab CE/EE affecting all versions starting from 15.5 prior to 16.9.7, starting from 16.10 prior to 16.10.5, and starting from 16.11 prior to 16.11.2. GitLab was vulnerable to Server Side Request Forgery when an attacker uses a malicious URL in the markdown  image value when importing a GitHub repository.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/432276
- https://hackerone.com/reports/2249268
- https://nvd.nist.gov/vuln/detail/CVE-2023-6195
