# [H] CVE-2016-0797

## Summary
Severity: High
Advisory: CVE-2016-0797
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-03-03
Source: https://osv.dev/vulnerability/CVE-2016-0797
Type: osv

## Details
Multiple integer overflows in OpenSSL 1.0.1 before 1.0.1s and 1.0.2 before 1.0.2g allow remote attackers to cause a denial of service (heap memory corruption or NULL pointer dereference) or possibly have unspecified other impact via a long digit string that is mishandled by the (1) BN_dec2bn or (2) BN_hex2bn function, related to crypto/bn/bn.h and crypto/bn/bn_print.c.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=c175308407858afff3fc8c2e5e085d94d12edc7d
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00019.html
