# [H] CVE-2021-44648

## Summary
Severity: High
Advisory: CVE-2021-44648
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-44648
Type: osv

## Details
GNOME gdk-pixbuf 2.42.6 is vulnerable to a heap-buffer overflow vulnerability when decoding the lzw compressed stream of image data in GIF files with lzw minimum code size equals to 12.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JEVTOGIJITK2N5AOOLKKMDIICZDQE6CH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PEKBMOO52RXONWKB6ZKKHTVPLF6WC3KF/
- https://www.debian.org/security/2022/dsa-5228
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/136
- https://sahildhar.github.io/blogpost/GdkPixbuf-Heap-Buffer-Overflow-in-lzw_decoder_new/
