# [M] CVE-2018-19572

## Summary
Severity: Medium
Advisory: CVE-2018-19572
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-10
Source: https://osv.dev/vulnerability/CVE-2018-19572
Type: osv

## Details
GitLab CE 8.17 and later and EE 8.3 and later have a symlink time-of-check-to-time-of-use race condition that would allow unauthorized access to files in the GitLab Pages chroot environment. This is fixed in versions 11.5.1, 11.4.8, and 11.3.11.

## References
- https://about.gitlab.com/2018/11/28/security-release-gitlab-11-dot-5-dot-1-released/
- https://gitlab.com/gitlab-org/gitlab-pages/issues/98
