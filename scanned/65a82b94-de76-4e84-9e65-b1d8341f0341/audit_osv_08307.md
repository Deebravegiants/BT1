# [M] CVE-2016-2178

## Summary
Severity: Medium
Advisory: CVE-2016-2178
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-20
Source: https://osv.dev/vulnerability/CVE-2016-2178
Type: osv

## Details
The dsa_sign_setup function in crypto/dsa/dsa_ossl.c in OpenSSL through 1.0.2h does not properly ensure the use of constant-time operations, which makes it easier for local users to discover a DSA private key via a timing side-channel attack.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=399944622df7bd81af62e67ea967c470534090e2
- http://eprint.iacr.org/2016/594.pdf
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
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2017-10/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2018-02/msg00032.html
- http://rhn.redhat.com/errata/RHSA-2016-1940.html
- http://rhn.redhat.com/errata/RHSA-2016-2957.html
- http://rhn.redhat.com/errata/RHSA-2017-1659.html
