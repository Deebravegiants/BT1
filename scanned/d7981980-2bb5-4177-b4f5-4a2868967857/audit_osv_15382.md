# [M] CVE-2019-15726

## Summary
Severity: Medium
Advisory: CVE-2019-15726
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-15726
Type: osv

## Details
An issue was discovered in GitLab Community and Enterprise Edition through 12.2.1. Embedded images and media files in markdown could be pointed to an arbitrary server, which would reveal the IP address of clients requesting the file from that server.

## References
- https://about.gitlab.com/2019/08/29/security-release-gitlab-12-dot-2-dot-3-released/
- https://gitlab.com/gitlab-org/gitlab-ce/issues/55115
