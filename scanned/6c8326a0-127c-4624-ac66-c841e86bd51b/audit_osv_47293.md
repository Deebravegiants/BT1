# [M] CVE-2016-2317

## Summary
Severity: Medium
Advisory: CVE-2016-2317
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/CVE-2016-2317
Type: osv

## Details
Multiple buffer overflows in GraphicsMagick 1.3.23 allow remote attackers to cause a denial of service (crash) via a crafted SVG file, related to the (1) TracePoint function in magick/render.c, (2) GetToken function in magick/utility.c, and (3) GetTransformTokens function in coders/svg.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00010.html
- http://www.debian.org/security/2016/dsa-3746
- http://www.openwall.com/lists/oss-security/2016/02/11/6
- http://www.openwall.com/lists/oss-security/2016/05/27/4
- http://www.openwall.com/lists/oss-security/2016/09/18/8
- http://www.securityfocus.com/bid/83241
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00037.html
- http://www.openwall.com/lists/oss-security/2016/05/20/4
- http://www.openwall.com/lists/oss-security/2016/05/31/3
- http://www.openwall.com/lists/oss-security/2016/09/07/4
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1306148
