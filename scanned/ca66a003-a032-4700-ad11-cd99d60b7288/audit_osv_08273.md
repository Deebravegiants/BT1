# [H] CVE-2016-2105

## Summary
Severity: High
Advisory: CVE-2016-2105
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-05
Source: https://osv.dev/vulnerability/CVE-2016-2105
Type: osv

## Details
Integer overflow in the EVP_EncodeUpdate function in crypto/evp/encode.c in OpenSSL before 1.0.1t and 1.0.2 before 1.0.2h allows remote attackers to cause a denial of service (heap memory corruption) via a large amount of binary data.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=5b814481f3573fa9677f3a31ee51322e2a22ee6a
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.apple.com/archives/security-announce/2016/Jul/msg00000.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183457.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/183607.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184605.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00030.html
