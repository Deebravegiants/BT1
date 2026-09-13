# [C] CVE-2022-25235

## Summary
Severity: Critical
Advisory: CVE-2022-25235
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2022-25235
Type: osv

## Details
xmltok_impl.c in Expat (aka libexpat) before 2.4.5 lacks certain validation of encoding, such as checks for whether a UTF-8 character is valid in a certain context.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-484086.pdf
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/25xxx/CVE-2022-25235.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3UFRBA3UQVIQKXTBUQXDWQOVWNBKLERU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y27XO3JMKAOMQZVPS3B4MJGEAHCZF5OM/
- https://nvd.nist.gov/vuln/detail/CVE-2022-25235
- https://security.gentoo.org/glsa/202209-24
- https://security.netapp.com/advisory/ntap-20220303-0008/
- https://www.debian.org/security/2022/dsa-5085
- https://github.com/libexpat/libexpat/pull/562
- http://www.openwall.com/lists/oss-security/2022/02/19/1
- https://lists.debian.org/debian-lts-announce/2022/03/msg00007.html
