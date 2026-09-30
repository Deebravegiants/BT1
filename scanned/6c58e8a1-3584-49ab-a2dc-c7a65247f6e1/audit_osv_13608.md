# [H] CVE-2018-20500

## Summary
Severity: High
Advisory: CVE-2018-20500
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-17
Source: https://osv.dev/vulnerability/CVE-2018-20500
Type: osv

## Details
An insecure permissions issue was discovered in GitLab Community and Enterprise Edition 9.4 and later but before 11.4.13, 11.5.x before 11.5.6, and 11.6.x before 11.6.1. The runner registration token in the CI/CD settings could not be reset. This was a security risk if one of the maintainers leaves the group and they know the token.

## References
- https://about.gitlab.com/2018/12/31/security-release-gitlab-11-dot-6-dot-1-released/
- https://about.gitlab.com/blog/categories/releases/
