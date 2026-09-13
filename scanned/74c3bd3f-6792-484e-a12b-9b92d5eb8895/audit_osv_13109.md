# [M] CVE-2018-17450

## Summary
Severity: Medium
Advisory: CVE-2018-17450
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2018-17450
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition before 11.1.7, 11.2.x before 11.2.4, and 11.3.x before 11.3.1. There is Server-Side Request Forgery (SSRF) via the Kubernetes integration, leading (for example) to disclosure of a GCP service token.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://about.gitlab.com/releases/2018/10/01/security-release-gitlab-11-dot-3-dot-1-released/
