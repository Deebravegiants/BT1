# [H] CVE-2017-7592

## Summary
Severity: High
Advisory: CVE-2017-7592
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7592
Type: osv

## Details
The putagreytile function in tif_getimage.c in LibTIFF 4.0.7 has a left-shift undefined behavior issue, which might allow remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image.

## References
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/97510
- https://security.gentoo.org/glsa/201709-27
- http://bugzilla.maptools.org/show_bug.cgi?id=2658
