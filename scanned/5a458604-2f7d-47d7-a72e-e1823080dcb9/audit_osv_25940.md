# [M] Glibc: potential use-after-free in getaddrinfo()

## Summary
Severity: Medium
Advisory: CVE-2023-4806
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-18
Source: https://osv.dev/vulnerability/CVE-2023-4806
Type: osv

## Details
A flaw has been identified in glibc. In an extremely rare situation, the getaddrinfo function may access memory that has been freed, resulting in an application crash. This issue is only exploitable when a NSS module implements only the _nss_*_gethostbyname2_r and _nss_*_getcanonname_r hooks without implementing the _nss_*_gethostbyname3_r hook. The resolved name should return a large number of IPv6 and IPv4, and the call to the getaddrinfo function should have the AF_INET6 address family with AI_CANONNAME, AI_ALL and AI_V4MAPPED as flags.

## References
- http://www.openwall.com/lists/oss-security/2023/10/03/4
- http://www.openwall.com/lists/oss-security/2023/10/03/5
- http://www.openwall.com/lists/oss-security/2023/10/03/6
- http://www.openwall.com/lists/oss-security/2023/10/03/8
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-831302.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4DBUQRRPB47TC3NJOUIBVWUGFHBJAFDL/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DFG4P76UHHZEWQ26FWBXG76N2QLKKPZA/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NDAQWHTSVOCOZ5K6KPIWKRT3JX4RTZUR/
- https://access.redhat.com/errata/RHSA-2023:5453
- https://access.redhat.com/errata/RHSA-2023:5455
- https://access.redhat.com/errata/RHSA-2023:7409
- https://access.redhat.com/security/cve/CVE-2023-4806
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4806.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4806
- https://security.gentoo.org/glsa/202310-03
- https://security.netapp.com/advisory/ntap-20240125-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=2237782
