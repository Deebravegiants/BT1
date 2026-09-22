# [H] CVE-2019-6788

## Summary
Severity: High
Advisory: CVE-2019-6788
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-09
Source: https://osv.dev/vulnerability/CVE-2019-6788
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition before 11.5.8, 11.6.x before 11.6.6, and 11.7.x before 11.7.1. It allows Information Disclosure (issue 3 of 6). For installations using GitHub or Bitbucket OAuth integrations, it is possible to use a covert redirect to obtain the user OAuth token for those services.

## References
- https://about.gitlab.com/2019/01/31/security-release-gitlab-11-dot-7-dot-3-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/56663
