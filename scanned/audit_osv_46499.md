# [H] CVE-2012-1610

## Summary
Severity: High
Advisory: CVE-2012-1610
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2012-06-05
Source: https://osv.dev/vulnerability/CVE-2012-1610
Type: osv

## Details
Integer overflow in the GetEXIFProperty function in magick/property.c in ImageMagick before 6.7.6-4 allows remote attackers to cause a denial of service (out-of-bounds read) via a large component count for certain EXIF tags in a JPEG image.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-0259.

## References
- http://lists.opensuse.org/opensuse-updates/2012-06/msg00001.html
- http://secunia.com/advisories/48974
- http://secunia.com/advisories/49043
- http://secunia.com/advisories/49317
- http://secunia.com/advisories/55035
- http://ubuntu.com/usn/usn-1435-1
- http://www.debian.org/security/2012/dsa-2462
- http://www.imagemagick.org/discourse-server/viewtopic.php?f=4&t=20629
- http://www.openwall.com/lists/oss-security/2012/04/04/6
- http://www.securityfocus.com/bid/52898
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-0259
- https://exchange.xforce.ibmcloud.com/vulnerabilities/74660
- http://lists.opensuse.org/opensuse-updates/2012-06/msg00001.html
- http://www.openwall.com/lists/oss-security/2012/04/04/6
- http://www.imagemagick.org/discourse-server/viewtopic.php?f=4&t=20629
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-0259
- http://www.imagemagick.org/discourse-server/viewtopic.php?f=4&t=20629
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-0259
- http://www.osvdb.org/81024
