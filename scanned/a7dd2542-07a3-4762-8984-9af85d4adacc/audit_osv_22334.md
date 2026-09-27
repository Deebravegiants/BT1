# [M] CVE-2022-25313

## Summary
Severity: Medium
Advisory: CVE-2022-25313
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2022-25313
Type: osv

## Details
In Expat (aka libexpat) before 2.4.5, an attacker can trigger stack exhaustion in build_model via a large nesting depth in the DTD element.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25313.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3UFRBA3UQVIQKXTBUQXDWQOVWNBKLERU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y27XO3JMKAOMQZVPS3B4MJGEAHCZF5OM/
- https://nvd.nist.gov/vuln/detail/CVE-2022-25313
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220303-0008/
- https://www.debian.org/security/2022/dsa-5085
- https://github.com/libexpat/libexpat/pull/558
- http://www.openwall.com/lists/oss-security/2022/02/19/1
- https://lists.debian.org/debian-lts-announce/2022/03/msg00007.html
