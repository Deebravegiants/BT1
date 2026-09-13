# [H] CVE-2018-18718

## Summary
Severity: High
Advisory: CVE-2018-18718
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-29
Source: https://osv.dev/vulnerability/CVE-2018-18718
Type: osv

## Details
An issue was discovered in gThumb through 3.6.2. There is a double-free vulnerability in the add_themes_from_dir method in dlg-contact-sheet.c because of two successive calls of g_free, each of which frees the same buffer.

## References
- https://lists.debian.org/debian-lts-announce/2018/11/msg00002.html
- https://gitlab.gnome.org/GNOME/gthumb/issues/18
