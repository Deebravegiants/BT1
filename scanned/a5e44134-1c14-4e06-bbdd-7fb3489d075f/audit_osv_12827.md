# [H] CVE-2018-15472

## Summary
Severity: High
Advisory: CVE-2018-15472
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2018-15472
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition before 11.1.7, 11.2.x before 11.2.4, and 11.3.x before 11.3.1. The diff formatter using rouge can block for a long time in Sidekiq jobs without any timeout.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://about.gitlab.com/releases/2018/10/01/security-release-gitlab-11-dot-3-dot-1-released/
