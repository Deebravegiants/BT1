# [M] CVE-2016-10167

## Summary
Severity: Medium
Advisory: CVE-2016-10167
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10167
Type: osv

## Details
The gdImageCreateFromGd2Ctx function in gd_gd2.c in the GD Graphics Library (aka libgd) before 2.2.4 allows remote attackers to cause a denial of service (application crash) via a crafted image file.

## References
- http://www.securitytracker.com/id/1037659
- https://www.tenable.com/security/tns-2017-04
- http://libgd.github.io/release-2.2.4.html
- http://www.debian.org/security/2017/dsa-3777
- http://www.securityfocus.com/bid/95869
- https://access.redhat.com/errata/RHSA-2017:3221
- https://access.redhat.com/errata/RHSA-2018:1296
- http://www.openwall.com/lists/oss-security/2017/01/26/1
- http://www.openwall.com/lists/oss-security/2017/01/28/6
- https://github.com/libgd/libgd/commit/fe9ed49dafa993e3af96b6a5a589efeea9bfb36f
