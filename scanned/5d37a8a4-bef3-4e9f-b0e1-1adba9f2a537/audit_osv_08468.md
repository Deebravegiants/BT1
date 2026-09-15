# [H] CVE-2016-3634

## Summary
Severity: High
Advisory: CVE-2016-3634
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-3634
Type: osv

## Details
The tagCompare function in tif_dirinfo.c in the thumbnail tool in LibTIFF 4.0.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) via vectors related to field_tag matching.

## References
- http://www.securityfocus.com/bid/93335
- http://www.openwall.com/lists/oss-security/2016/04/08/13
- https://security.gentoo.org/glsa/201701-16
- http://bugzilla.maptools.org/show_bug.cgi?id=2547
