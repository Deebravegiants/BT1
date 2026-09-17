# [H] CVE-2021-27219

## Summary
Severity: High
Advisory: CVE-2021-27219
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/CVE-2021-27219
Type: osv

## Details
An issue was discovered in GNOME GLib before 2.66.6 and 2.67.x before 2.67.3. The function g_bytes_new has an integer overflow on 64-bit platforms due to an implicit cast from 64 bits to 32 bits. The overflow could potentially lead to memory corruption.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2REA7RVKN7ZHRLJOEGBRQKJIPZQPAELZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JJMPNDO4GDVURYQFYKFOWY5HAF4FTEPN/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00006.html
- https://security.gentoo.org/glsa/202107-13
- https://security.netapp.com/advisory/ntap-20210319-0004/
- https://gitlab.gnome.org/GNOME/glib/-/issues/2319
