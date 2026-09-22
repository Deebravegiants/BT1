# [H] CVE-2019-18837

## Summary
Severity: High
Advisory: CVE-2019-18837
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-18837
Type: osv

## Details
An issue was discovered in crun before 0.10.5. With a crafted image, it doesn't correctly check whether a target is a symlink, resulting in access to files outside of the container. This occurs in libcrun/linux.c and libcrun/chroot_realpath.c.

## References
- https://github.com/containers/crun/releases/tag/0.10.5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DTA5SJUAKQUK6HRY2CZVJUIZP5BO3EOG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ITB2UNEGHXZUR3ATYHWPSK5LJB36N7AP/
- https://github.com/containers/crun/pull/173
