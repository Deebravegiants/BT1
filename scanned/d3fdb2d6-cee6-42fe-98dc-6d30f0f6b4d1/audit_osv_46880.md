# [H] CVE-2015-7557

## Summary
Severity: High
Advisory: CVE-2015-7557
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-20
Source: https://osv.dev/vulnerability/CVE-2015-7557
Type: osv

## Details
The _rsvg_node_poly_build_path function in rsvg-shapes.c in librsvg before 2.40.7 allows context-dependent attackers to cause a denial of service (out-of-bounds heap read) via an odd number of elements in a coordinate pair in an SVG document.

## References
- https://git.gnome.org/browse/librsvg/commit/rsvg-shapes.c?id=40af93e6eb1c94b90c3b9a0b87e0840e126bb8df
- https://git.gnome.org/browse/librsvg/tree/NEWS
- http://www.openwall.com/lists/oss-security/2015/12/21/5
