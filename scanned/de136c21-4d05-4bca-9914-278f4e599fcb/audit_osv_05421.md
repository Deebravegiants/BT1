# [H] Incorrect Authorization in GitLab

## Summary
Severity: High
Advisory: BIT-gitlab-2024-0199
Aliases: CVE-2024-0199
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-0199
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=16.9.0 <16.9.2

## Details
An authorization bypass vulnerability was discovered in GitLab affecting versions 11.3 prior to 16.7.7, 16.7.6 prior to 16.8.4, and 16.8.3 prior to 16.9.2. An attacker could bypass CODEOWNERS by utilizing a crafted payload in an old feature branch to perform malicious actions.

## References
- https://about.gitlab.com/releases/2024/03/06/security-release-gitlab-16-9-2-released/
- https://gitlab.com/gitlab-org/gitlab/-/issues/436977
- https://hackerone.com/reports/2295423
- https://nvd.nist.gov/vuln/detail/CVE-2024-0199
