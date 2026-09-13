# [C] Incorrect Authorization in GitLab

## Summary
Severity: Critical
Advisory: BIT-gitlab-2024-2743
Aliases: CVE-2024-2743
Ecosystem: Bitnami
Published: 2024-09-14
Source: https://osv.dev/vulnerability/BIT-gitlab-2024-2743
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=17.3.0 <17.3.2

## Details
An issue was discovered in GitLab-EE starting with version 13.3 before 17.1.7, 17.2 before 17.2.5, and 17.3 before 17.3.2 that would allow an attacker to modify an on-demand DAST scan without permissions and leak variables.

## References
- https://gitlab.com/gitlab-org/gitlab/-/issues/451014
- https://hackerone.com/reports/2411756
- https://about.gitlab.com/releases/2024/09/11/patch-release-gitlab-17-3-2-released/
- https://nvd.nist.gov/vuln/detail/CVE-2024-2743
