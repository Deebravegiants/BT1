# [M] CVE-2019-19312

## Summary
Severity: Medium
Advisory: CVE-2019-19312
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2020-01-05
Source: https://osv.dev/vulnerability/CVE-2019-19312
Type: osv

## Details
GitLab EE 8.14 through 12.5, 12.4.3, and 12.3.6 has Incorrect Access Control. After a project changed to private, previously forked repositories were still able to get information about the private project through the API.

## References
- https://about.gitlab.com/blog/2019/11/27/security-release-gitlab-12-5-1-released/
- https://about.gitlab.com/blog/categories/releases/
- https://gitlab.com/gitlab-org/gitlab/issues/28802
