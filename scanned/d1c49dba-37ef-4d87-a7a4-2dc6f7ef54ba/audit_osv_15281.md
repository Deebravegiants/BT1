# [M] CVE-2019-14944

## Summary
Severity: Medium
Advisory: CVE-2019-14944
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2023-04-16
Source: https://osv.dev/vulnerability/CVE-2019-14944
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition before 11.11.8, 12 before 12.0.6, and 12.1 before 12.1.6. Gitaly allows injection of command-line flags. This sometimes leads to privilege escalation or remote code execution.

## References
- https://about.gitlab.com/blog/categories/releases/
- https://about.gitlab.com/releases/2019/08/12/critical-security-release-gitlab-12-dot-1-dot-6-released/
- https://gitlab.com/gitlab-org/gitaly/issues/1801
- https://gitlab.com/gitlab-org/gitaly/issues/1802
