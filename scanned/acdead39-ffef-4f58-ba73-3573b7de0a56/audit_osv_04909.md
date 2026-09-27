# [H] BIT-gitlab-2020-11505

## Summary
Severity: High
Advisory: BIT-gitlab-2020-11505
Aliases: CVE-2020-11505
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-11505
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=12.9.0 <12.9.3

## Details
An issue was discovered in GitLab Community Edition (CE) and Enterprise Edition (EE) before 12.7.9, 12.8.x before 12.8.9, and 12.9.x before 12.9.3. A Workhorse bypass could lead to NuGet package and file disclosure (Exposure of Sensitive Information) via request smuggling.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://about.gitlab.com/releases/2020/04/14/critical-security-release-gitlab-12-dot-9-dot-3-released/
- https://nvd.nist.gov/vuln/detail/CVE-2020-11505
