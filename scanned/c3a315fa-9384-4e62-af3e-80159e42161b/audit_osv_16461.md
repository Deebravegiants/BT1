# [M] CVE-2019-7155

## Summary
Severity: Medium
Advisory: CVE-2019-7155
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-16
Source: https://osv.dev/vulnerability/CVE-2019-7155
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition 9.x, 10.x, and 11.x before 11.5.8, 11.6.x before 11.6.6, and 11.7.x before 11.7.1. It has Incorrect Access Control. A user retains their role within a project in a private group after being removed from the group, if their privileges within the project are different from the group.

## References
- https://about.gitlab.com/2019/01/31/security-release-gitlab-11-dot-7-dot-3-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/42726
