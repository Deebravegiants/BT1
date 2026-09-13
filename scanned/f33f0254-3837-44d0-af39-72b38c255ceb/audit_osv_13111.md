# [C] CVE-2018-17452

## Summary
Severity: Critical
Advisory: CVE-2018-17452
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2018-17452
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition before 11.1.7, 11.2.x before 11.2.4, and 11.3.x before 11.3.1. There is Server-Side Request Forgery (SSRF) via a loopback address to the validate_localhost function in url_blocker.rb.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://about.gitlab.com/releases/2018/10/01/security-release-gitlab-11-dot-3-dot-1-released/
