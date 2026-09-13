# [C] Deserialization of Untrusted Data in Apache Batik

## Summary
Severity: Critical
Advisory: GHSA-25gw-4pcc-45cf
CVE: CVE-2018-8013
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-25gw-4pcc-45cf
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:batik` — affected >=1.0 <1.10

## Details
In Apache Batik 1.x before 1.10, when deserializing subclass of `AbstractDocument`, the class takes a string from the inputStream as the class name which then use it to call the no-arg constructor of the class. Fix was to check the class type before calling newInstance in deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8013
- https://github.com/apache/xmlgraphics-batik/commit/f91125b26a6ca2b7a1195f1842360bed03629839
- https://xmlgraphics.apache.org/security.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.debian.org/security/2018/dsa-4215
- https://usn.ubuntu.com/3661-1
- https://ubuntu.com/security/CVE-2018-8013
- https://security.gentoo.org/glsa/202401-11
- https://mail-archives.apache.org/mod_mbox/xmlgraphics-batik-dev/201805.mbox/%3c000701d3f28f%24d01860a0%24704921e0%24%40gmail.com%3e
- https://mail-archives.apache.org/mod_mbox/xmlgraphics-batik-dev/201805.mbox/%3c000701d3f28f$d01860a0$704921e0$@gmail.com%3e
- https://lists.debian.org/debian-lts-announce/2018/05/msg00016.html
- https://lists.apache.org/thread.html/rc0a31867796043fbe59113fb654fe8b13309fe04f8935acb8d0fab19@%3Ccommits.xmlgraphics.apache.org%3E
- https://lists.apache.org/thread.html/rc0a31867796043fbe59113fb654fe8b13309fe04f8935acb8d0fab19%40%3Ccommits.xmlgraphics.apache.org%3E
- https://lists.apache.org/thread.html/r9e90b4d1cf6ea87a79bb506541140dfbf4801f4463a7cee08126ee44@%3Ccommits.xmlgraphics.apache.org%3E
- https://lists.apache.org/thread.html/r9e90b4d1cf6ea87a79bb506541140dfbf4801f4463a7cee08126ee44%40%3Ccommits.xmlgraphics.apache.org%3E
- https://issues.apache.org/jira/browse/BATIK-1222
