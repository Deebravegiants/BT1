# [M] CVE-2013-7447

## Summary
Severity: Medium
Advisory: CVE-2013-7447
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-17
Source: https://osv.dev/vulnerability/CVE-2013-7447
Type: osv

## Details
Integer overflow in the gdk_cairo_set_source_pixbuf function in gdk/gdkcairo.c in GTK+ before 3.9.8, as used in eom, gnome-photos, eog, gambas3, thunar, pinpoint, and possibly other applications, allows remote attackers to cause a denial of service (crash) via a large image file, which triggers a large memory allocation.

## References
- http://www.ubuntu.com/usn/USN-2898-1
- http://www.ubuntu.com/usn/USN-2898-2
- https://git.gnome.org/browse/gtk+/tree/NEWS
- https://bugzilla.gnome.org/show_bug.cgi?id=703220
- https://github.com/mate-desktop/eom/issues/93
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00010.html
- http://www.openwall.com/lists/oss-security/2016/02/10/2
- http://www.openwall.com/lists/oss-security/2016/02/10/6
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/83239
- https://bugs.launchpad.net/ubuntu/+source/gtk+2.0/+bug/1540811
- https://git.gnome.org/browse/gtk+/commit?id=894b1ae76a32720f4bb3d39cf460402e3ce331d6
