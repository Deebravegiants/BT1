# [M] CVE-2019-12449

## Summary
Severity: Medium
Advisory: CVE-2019-12449
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-05-29
Source: https://osv.dev/vulnerability/CVE-2019-12449
Type: osv

## Details
An issue was discovered in GNOME gvfs 1.29.4 through 1.41.2. daemon/gvfsbackendadmin.c mishandles a file's user and group ownership during move (and copy with G_FILE_COPY_ALL_METADATA) operations from admin:// to file:// URIs, because root privileges are unavailable.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FP6BFQUPQRVRRFIYHFWWB6RHJNEB4LGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M2DQVOL5H5BVLXYCEB763DCIYJQ7ZUQ2/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00009.html
- http://www.openwall.com/lists/oss-security/2019/07/09/3
- https://usn.ubuntu.com/4053-1/
- https://gitlab.gnome.org/GNOME/gvfs/commit/409619412e11be146a31b9a99ed965925f1aabb8
