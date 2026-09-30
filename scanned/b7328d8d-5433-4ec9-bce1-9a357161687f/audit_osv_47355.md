# [H] CVE-2016-3190

## Summary
Severity: High
Advisory: CVE-2016-3190
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-21
Source: https://osv.dev/vulnerability/CVE-2016-3190
Type: osv

## Details
The fill_xrgb32_lerp_opaque_spans function in cairo-image-compositor.c in cairo before 1.14.2 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a negative span length.

## References
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00029.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1318977
- https://mail.gnome.org/archives/gnome-announce-list/2015-March/msg00047.html
- https://cgit.freedesktop.org/cairo/patch/src/cairo-image-compositor.c?id=5c82d91a5e15d29b1489dcb413b24ee7fdf59934
