# [M] CVE-2021-28153

## Summary
Severity: Medium
Advisory: CVE-2021-28153
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-28153
Type: osv

## Details
An issue was discovered in GNOME GLib before 2.66.8. When g_file_replace() is used with G_FILE_CREATE_REPLACE_DESTINATION to replace a path that is a dangling symlink, it incorrectly also creates the target of the symlink as an empty file, which could conceivably have security relevance if the symlink is attacker-controlled. (If the path is a symlink to a file that already exists, then the contents of that file correctly remain unchanged.)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6RXTD5HCP2K4AAUSWWZTBKQNHRCTAEOF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ICUTQPHZNZWX2DZR46QFLQZRHVMHIILJ/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00006.html
- https://security.gentoo.org/glsa/202107-13
- https://security.netapp.com/advisory/ntap-20210416-0003/
- https://gitlab.gnome.org/GNOME/glib/-/issues/2325
