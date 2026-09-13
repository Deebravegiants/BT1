# [H] CVE-2016-6304

## Summary
Severity: High
Advisory: CVE-2016-6304
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6304
Type: osv

## Details
Multiple memory leaks in t1_lib.c in OpenSSL before 1.0.1u, 1.0.2 before 1.0.2i, and 1.1.0 before 1.1.0a allow remote attackers to cause a denial of service (memory consumption) via large OCSP Status Request extensions.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=2c0d295e26306e15a92eb23a84a1802005c1c137
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2016-09/msg00031.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-10/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2016-11/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-11/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00032.html
- http://packetstormsecurity.com/files/139091/OpenSSL-x509-Parsing-Double-Free-Invalid-Free.html
- http://rhn.redhat.com/errata/RHSA-2016-1940.html
