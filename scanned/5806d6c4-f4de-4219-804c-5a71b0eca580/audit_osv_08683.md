# [H] CVE-2016-5300

## Summary
Severity: High
Advisory: CVE-2016-5300
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-5300
Type: osv

## Details
The XML parser in Expat does not use sufficient entropy for hash initialization, which allows context-dependent attackers to cause a denial of service (CPU consumption) via crafted identifiers in an XML document.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2012-0876.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10365
- https://lists.apache.org/thread.html/r58af02e294bd07f487e2c64ffc0a29b837db5600e33b6e698b9d696b%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf4c02775860db415b4955778a131c2795223f61cb8c6a450893651e4%40%3Cissues.bookkeeper.apache.org%3E
- http://www.debian.org/security/2016/dsa-3597
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/91159
- http://www.ubuntu.com/usn/USN-3010-1
- https://security.gentoo.org/glsa/201701-21
- https://source.android.com/security/bulletin/2016-11-01.html
- https://www.tenable.com/security/tns-2016-20
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.openwall.com/lists/oss-security/2016/06/04/4
- http://www.openwall.com/lists/oss-security/2016/06/04/5
