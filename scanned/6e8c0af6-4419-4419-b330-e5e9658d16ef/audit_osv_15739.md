# [M] CVE-2019-19308

## Summary
Severity: Medium
Advisory: CVE-2019-19308
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-27
Source: https://osv.dev/vulnerability/CVE-2019-19308
Type: osv

## Details
In text_to_glyphs in sushi-font-widget.c in gnome-font-viewer 3.34.0, there is a NULL pointer dereference while parsing a TTF font file that lacks a name section (due to a g_strconcat call that returns NULL).

## References
- https://github.com/GNOME/gnome-font-viewer/blob/919dfbe684b75904563b8c6723c9778a4e00aad7/src/sushi-font-widget.c#L115-L117
- https://gitlab.gnome.org/GNOME/gnome-font-viewer/issues/17
