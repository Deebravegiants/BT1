# [M] CVE-2016-5315

## Summary
Severity: Medium
Advisory: CVE-2016-5315
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-07
Source: https://osv.dev/vulnerability/CVE-2016-5315
Type: osv

## Details
The setByteArray function in tif_dir.c in libtiff 4.0.6 and earlier allows remote attackers to cause a denial of service (out-of-bounds read) via a crafted tiff image.

## References
- http://www.debian.org/security/2017/dsa-3762
- http://www.openwall.com/lists/oss-security/2016/06/15/2
- http://www.securityfocus.com/bid/91204
- https://security.gentoo.org/glsa/201701-16
- https://bugzilla.redhat.com/show_bug.cgi?id=1346694
