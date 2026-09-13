# [H] CVE-2021-27218

## Summary
Severity: High
Advisory: CVE-2021-27218
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/CVE-2021-27218
Type: osv

## Details
An issue was discovered in GNOME GLib before 2.66.7 and 2.67.x before 2.67.4. If g_byte_array_new_take() was called with a buffer of 4GB or more on a 64-bit platform, the length would be truncated modulo 2**32, causing unintended length truncation.

## References
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2REA7RVKN7ZHRLJOEGBRQKJIPZQPAELZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JJMPNDO4GDVURYQFYKFOWY5HAF4FTEPN/
- https://lists.debian.org/debian-lts-announce/2022/06/msg00006.html
- https://security.gentoo.org/glsa/202107-13
- https://security.netapp.com/advisory/ntap-20210319-0004/
- https://gitlab.gnome.org/GNOME/glib/-/merge_requests/1942
- https://gitlab.gnome.org/GNOME/glib/-/merge_requests/1944
