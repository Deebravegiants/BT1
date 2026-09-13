# [H] CVE-2019-15730

## Summary
Severity: High
Advisory: CVE-2019-15730
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-15730
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition 8.14 through 12.2.1. The Jira integration contains a SSRF vulnerability as a result of a bypass of the current protection mechanisms against this type of attack, which would allow sending requests to any resources accessible in the local network by the GitLab server.

## References
- https://about.gitlab.com/2019/08/29/security-release-gitlab-12-dot-2-dot-3-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/61349
