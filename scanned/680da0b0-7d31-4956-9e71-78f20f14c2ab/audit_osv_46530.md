# [M] CVE-2012-6702

## Summary
Severity: Medium
Advisory: CVE-2012-6702
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2012-6702
Type: osv

## Details
Expat, when used in a parser that has not called XML_SetHashSalt or passed it a seed of 0, makes it easier for context-dependent attackers to defeat cryptographic protection mechanisms via vectors involving use of the srand function.

## References
- http://www.debian.org/security/2016/dsa-3597
- http://www.ubuntu.com/usn/USN-3010-1
- https://security.gentoo.org/glsa/201701-21
- http://www.openwall.com/lists/oss-security/2016/06/03/8
- http://www.openwall.com/lists/oss-security/2016/06/04/1
- http://www.securityfocus.com/bid/91483
- https://source.android.com/security/bulletin/2016-11-01.html
- https://www.tenable.com/security/tns-2016-20
