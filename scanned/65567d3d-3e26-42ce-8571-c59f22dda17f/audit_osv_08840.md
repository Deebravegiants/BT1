# [M] CVE-2016-6306

## Summary
Severity: Medium
Advisory: CVE-2016-6306
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-26
Source: https://osv.dev/vulnerability/CVE-2016-6306
Type: osv

## Details
The certificate parser in OpenSSL before 1.0.1u and 1.0.2 before 1.0.2i might allow remote attackers to cause a denial of service (out-of-bounds read) via crafted certificate operations, related to s3_clnt.c and s3_srvr.c.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://git.openssl.org/?p=openssl.git%3Ba=commit%3Bh=52e623c4cb06fffa9d5e75c60b34b4bc130b12e9
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
- http://seclists.org/fulldisclosure/2017/Jul/31
- http://www-01.ibm.com/support/docview.wss?uid=swg21995039
- http://www.debian.org/security/2016/dsa-3673
