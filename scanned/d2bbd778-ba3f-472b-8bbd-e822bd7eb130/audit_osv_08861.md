# [H] CVE-2016-6352

## Summary
Severity: High
Advisory: CVE-2016-6352
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-6352
Type: osv

## Details
The OneLine32 function in io-ico.c in gdk-pixbuf before 2.35.3 allows remote attackers to cause a denial of service (out-of-bounds write and crash) via crafted dimensions in an ICO file.

## References
- https://lists.debian.org/debian-lts-announce/2019/12/msg00025.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00040.html
- http://www.openwall.com/lists/oss-security/2016/07/26/11
- http://www.ubuntu.com/usn/USN-3085-1
- https://git.gnome.org/browse/gdk-pixbuf/tree/NEWS?id=640134c46221689d263369872937192e4484c83b
- https://bugzilla.gnome.org/show_bug.cgi?id=769170
- http://www.openwall.com/lists/oss-security/2016/07/13/11
- https://git.gnome.org/browse/gdk-pixbuf/commit/?id=88af50a864195da1a4f7bda5f02539704fbda599
