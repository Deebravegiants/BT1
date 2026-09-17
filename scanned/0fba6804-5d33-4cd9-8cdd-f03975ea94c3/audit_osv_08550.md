# [H] CVE-2016-4348

## Summary
Severity: High
Advisory: CVE-2016-4348
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-20
Source: https://osv.dev/vulnerability/CVE-2016-4348
Type: osv

## Details
The _rsvg_css_normalize_font_size function in librsvg 2.40.2 allows context-dependent attackers to cause a denial of service (stack consumption and application crash) via circular definitions in an SVG document.

## References
- http://www.openwall.com/lists/oss-security/2016/04/28/4
- http://www.openwall.com/lists/oss-security/2016/04/28/7
- http://www.openwall.com/lists/oss-security/2016/04/30/3
- http://www.openwall.com/lists/oss-security/2016/05/10/15
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00079.html
- http://www.debian.org/security/2016/dsa-3584
- https://git.gnome.org/browse/librsvg/commit/?id=d1c9191949747f6dcfd207831d15dd4ba00e31f2
