# [H] CVE-2019-15583

## Summary
Severity: High
Advisory: CVE-2019-15583
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-01-28
Source: https://osv.dev/vulnerability/CVE-2019-15583
Type: osv

## Details
An information disclosure exists in < 12.3.2, < 12.2.6, and < 12.1.12 for GitLab Community Edition (CE) and Enterprise Edition (EE). When an issue was moved to a public project from a private one, the associated private labels and the private project namespace would be disclosed through the GitLab API.

## References
- https://about.gitlab.com/blog/2019/09/30/security-release-gitlab-12-dot-3-dot-2-released/
- https://hackerone.com/reports/643854
