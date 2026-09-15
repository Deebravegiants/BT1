# [C] CVE-2016-0705

## Summary
Severity: Critical
Advisory: CVE-2016-0705
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-03-03
Source: https://osv.dev/vulnerability/CVE-2016-0705
Type: osv

## Details
Double free vulnerability in the dsa_priv_decode function in crypto/dsa/dsa_ameth.c in OpenSSL 1.0.1 before 1.0.1s and 1.0.2 before 1.0.2g allows remote attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact via a malformed DSA private key.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=6c88c71b4e4825c7bc0489306d062d017634eb88
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178358.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178817.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00019.html
- http://marc.info/?l=bugtraq&m=145889460330120&w=2
- http://marc.info/?l=bugtraq&m=145983526810210&w=2
- http://marc.info/?l=bugtraq&m=146108058503441&w=2
