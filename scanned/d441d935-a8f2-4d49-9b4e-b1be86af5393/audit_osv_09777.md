# [H] CVE-2017-11464

## Summary
Severity: High
Advisory: CVE-2017-11464
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-19
Source: https://osv.dev/vulnerability/CVE-2017-11464
Type: osv

## Details
A SIGFPE is raised in the function box_blur_line of rsvg-filter.c in GNOME librsvg 2.40.17 during an attempted parse of a crafted SVG file, because of incorrect protection against division by zero.

## References
- http://www.securityfocus.com/bid/99956
- https://lists.debian.org/debian-lts-announce/2020/07/msg00016.html
- https://usn.ubuntu.com/4436-1/
- https://bugzilla.gnome.org/show_bug.cgi?id=783835
- https://git.gnome.org/browse/librsvg/commit/?id=ecf9267a24b2c3c0cd211dbdfa9ef2232511972a
- https://github.com/GNOME/librsvg/commit/ecf9267a24b2c3c0cd211dbdfa9ef2232511972a
