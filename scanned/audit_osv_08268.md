# [M] CVE-2016-2073

## Summary
Severity: Medium
Advisory: CVE-2016-2073
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/CVE-2016-2073
Type: osv

## Details
The htmlParseNameComplex function in HTMLparser.c in libxml2 allows attackers to cause a denial of service (out-of-bounds read) via a crafted XML document.

## References
- http://www.openwall.com/lists/oss-security/2016/01/25/6
- http://www.openwall.com/lists/oss-security/2016/01/26/7
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- http://www.securityfocus.com/bid/85267
- http://www.securitytracker.com/id/1035011
- http://www.ubuntu.com/usn/USN-2994-1
- https://security.gentoo.org/glsa/201701-37
- https://www.debian.org/security/2016/dsa-3593
