# [H] CVE-2019-12448

## Summary
Severity: High
Advisory: CVE-2019-12448
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/CVE-2019-12448
Type: osv

## Details
An issue was discovered in GNOME gvfs 1.29.4 through 1.41.2. daemon/gvfsbackendadmin.c has race conditions because the admin backend doesn't implement query_info_on_read/write.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00009.html
- http://www.openwall.com/lists/oss-security/2019/07/09/3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FP6BFQUPQRVRRFIYHFWWB6RHJNEB4LGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M2DQVOL5H5BVLXYCEB763DCIYJQ7ZUQ2/
- https://usn.ubuntu.com/4053-1/
- https://gitlab.gnome.org/GNOME/gvfs/commit/764e9af7522e3096c0f44613c330377d31c9bbb5
