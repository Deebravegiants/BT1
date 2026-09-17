# [H] CVE-2016-8602

## Summary
Severity: High
Advisory: CVE-2016-8602
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-8602
Type: osv

## Details
The .sethalftone5 function in psi/zht2.c in Ghostscript before 9.21 allows remote attackers to cause a denial of service (application crash) or possibly execute arbitrary code via a crafted Postscript document that calls .sethalftone5 with an empty operand stack.

## References
- http://git.ghostscript.com/?p=ghostpdl.git%3Ba=commitdiff%3Bh=f5c7555c303
- https://security.gentoo.org/glsa/201702-31
- http://rhn.redhat.com/errata/RHSA-2017-0013.html
- http://www.securityfocus.com/bid/95311
- http://rhn.redhat.com/errata/RHSA-2017-0014.html
- http://www.debian.org/security/2016/dsa-3691
- https://bugs.ghostscript.com/show_bug.cgi?id=697203
- http://www.openwall.com/lists/oss-security/2016/10/11/5
- http://www.openwall.com/lists/oss-security/2016/10/11/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1383940
- https://ghostscript.com/doc/9.21/History9.htm
