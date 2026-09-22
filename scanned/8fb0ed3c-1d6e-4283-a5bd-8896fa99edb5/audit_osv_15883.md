# [H] CVE-2019-20326

## Summary
Severity: High
Advisory: CVE-2019-20326
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2019-20326
Type: osv

## Details
A heap-based buffer overflow in _cairo_image_surface_create_from_jpeg() in extensions/cairo_io/cairo-image-surface-jpeg.c in GNOME gThumb before 3.8.3 and Linux Mint Pix before 2.4.5 allows attackers to cause a crash and potentially execute arbitrary code via a crafted JPEG file.

## References
- https://gitlab.gnome.org/GNOME/gthumb/commit/ca8f528209ab78935c30e42fe53bdf1a24f3cb44
- https://gitlab.gnome.org/GNOME/gthumb/commits/master/extensions/cairo_io/cairo-image-surface-jpeg.c
- https://lists.debian.org/debian-lts-announce/2021/08/msg00027.html
- https://security.gentoo.org/glsa/202008-05
- https://gitlab.gnome.org/GNOME/gthumb/commit/4faa5ce2358812d23a1147953ee76f59631590ad
- https://github.com/Fysac/CVE-2019-20326
