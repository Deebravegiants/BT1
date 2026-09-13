# [H] CVE-2017-5884

## Summary
Severity: High
Advisory: CVE-2017-5884
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-28
Source: https://osv.dev/vulnerability/CVE-2017-5884
Type: osv

## Details
gtk-vnc before 0.7.0 does not properly check boundaries of subrectangle-containing tiles, which allows remote servers to execute arbitrary code via the src x, y coordinates in a crafted (1) rre, (2) hextile, or (3) copyrect tile.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LGPQ5MQR6SN4DYTEFACHP2PP5RR26KYK/
- http://www.openwall.com/lists/oss-security/2017/02/03/5
- http://www.openwall.com/lists/oss-security/2017/02/05/5
- http://www.securityfocus.com/bid/96016
- https://access.redhat.com/errata/RHSA-2017:2258
- https://bugzilla.gnome.org/show_bug.cgi?id=778048
- https://git.gnome.org/browse/gtk-vnc/commit/?id=ea0386933214c9178aaea9f2f85049ea3fa3e14a
