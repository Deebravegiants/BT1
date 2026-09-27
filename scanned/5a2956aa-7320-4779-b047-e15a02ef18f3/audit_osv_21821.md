# [H] CVE-2021-46829

## Summary
Severity: High
Advisory: CVE-2021-46829
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-07-24
Source: https://osv.dev/vulnerability/CVE-2021-46829
Type: osv

## Details
GNOME GdkPixbuf (aka GDK-PixBuf) before 2.42.8 allows a heap-based buffer overflow when compositing or clearing frames in GIF files, as demonstrated by io-gif-animation.c composite_frame. This overflow is controllable and could be abused for code execution, especially on 32-bit systems.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M5IHHEYFD6GDZVALKIPPRD2U4JNZUZWR/
- http://www.openwall.com/lists/oss-security/2022/07/25/1
- https://www.debian.org/security/2022/dsa-5228
- https://www.openwall.com/lists/oss-security/2022/07/23/1
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/190
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/commit/5398f04d772f7f8baf5265715696ed88db0f0512
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/commit/bca00032ad68d0b0aa2c1f7558db931e52bd9cd2
- https://github.com/pedrib/PoC/blob/master/fuzzing/CVE-2021-46829/CVE-2021-46829.md
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/merge_requests/121
