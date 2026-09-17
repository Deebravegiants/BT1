# [M] CVE-2016-4008

## Summary
Severity: Medium
Advisory: CVE-2016-4008
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-4008
Type: osv

## Details
The _asn1_extract_der_octet function in lib/decoding.c in GNU Libtasn1 before 4.8, when used without the ASN1_DECODE_FLAG_STRICT_DER flag, allows remote attackers to cause a denial of service (infinite recursion) via a crafted certificate.

## References
- http://git.savannah.gnu.org/gitweb/?p=libtasn1.git%3Ba=commit%3Bh=a6e0a0b58f5cdaf4e9beca5bce69c09808cbb625
- http://git.savannah.gnu.org/gitweb/?p=libtasn1.git%3Ba=commit%3Bh=f435825c0f527a8e52e6ffbc3ad0bc60531d537e
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182299.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182907.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183221.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00047.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00097.html
- http://www.openwall.com/lists/oss-security/2016/04/11/3
- https://lists.gnu.org/archive/html/help-libtasn1/2016-04/msg00009.html
- http://www.debian.org/security/2016/dsa-3568
- http://www.ubuntu.com/usn/USN-2957-1
- http://www.ubuntu.com/usn/USN-2957-2
- https://security.gentoo.org/glsa/201703-05
