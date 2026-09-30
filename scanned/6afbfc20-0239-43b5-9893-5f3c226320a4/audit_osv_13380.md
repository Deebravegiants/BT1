# [H] CVE-2018-19576

## Summary
Severity: High
Advisory: CVE-2018-19576
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2018-19576
Type: osv

## Details
GitLab CE/EE, versions 8.6 up to 11.x before 11.3.11, 11.4 before 11.4.8, and 11.5 before 11.5.1, are vulnerable to an access control issue that allows a Guest user to make changes to or delete their own comments on an issue, after the issue was made Confidential.

## References
- https://about.gitlab.com/2018/11/28/security-release-gitlab-11-dot-5-dot-1-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/51238
