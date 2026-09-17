# [M] CVE-2012-1186

## Summary
Severity: Medium
Advisory: CVE-2012-1186
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2012-06-05
Source: https://osv.dev/vulnerability/CVE-2012-1186
Type: osv

## Details
Integer overflow in the SyncImageProfiles function in profile.c in ImageMagick 6.7.5-8 and earlier allows remote attackers to cause a denial of service (infinite loop) via crafted IOP tag offsets in the IFD in an image.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-0248.

## References
- http://lists.opensuse.org/opensuse-updates/2012-06/msg00001.html
- http://secunia.com/advisories/47926
- http://secunia.com/advisories/48974
- http://secunia.com/advisories/49043
- http://secunia.com/advisories/49317
- http://ubuntu.com/usn/usn-1435-1
- http://www.debian.org/security/2012/dsa-2462
- http://www.openwall.com/lists/oss-security/2012/03/19/5
- http://www.securityfocus.com/bid/51957
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-1186
- https://exchange.xforce.ibmcloud.com/vulnerabilities/76139
- http://lists.opensuse.org/opensuse-updates/2012-06/msg00001.html
- http://www.openwall.com/lists/oss-security/2012/03/19/5
- http://www.openwall.com/lists/oss-security/2012/03/19/5
- http://www.securityfocus.com/bid/51957
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-1186
- http://trac.imagemagick.org/changeset/6998/ImageMagick/branches/ImageMagick-6.7.5/magick/profile.c
- http://www.osvdb.org/80555
