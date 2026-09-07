# [M] Roundup vulnerability related to Cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-c3qv-mf8h-434r
CVE: CVE-2008-1474
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-c3qv-mf8h-434r
Type: github-advisory

## Affected
- PyPI: `roundup` — affected >=0 <1.4.4

## Details
Multiple unspecified vulnerabilities in Roundup before 1.4.4 have unknown impact and attack vectors, some of which may be related to cross-site scripting (XSS).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-1474
- https://github.com/roundup-tracker/roundup/commit/151ffd3367e7af563a92aabb3a8034a0f49063d9
- https://bugzilla.redhat.com/show_bug.cgi?id=436546
- https://exchange.xforce.ibmcloud.com/vulnerabilities/41241
- https://github.com/pypa/advisory-database/tree/main/vulns/roundup/PYSEC-2008-9.yaml
- https://github.com/roundup-tracker/roundup
- https://lists.debian.org/debian-security-announce/2008/msg00125.html
- https://www.redhat.com/archives/fedora-package-announce/2008-March/msg00264.html
- https://www.redhat.com/archives/fedora-package-announce/2008-March/msg00375.html
- http://roundup.cvs.sourceforge.net/roundup/roundup/CHANGES.txt?revision=1.939&view=markup
- http://security.gentoo.org/glsa/glsa-200805-21.xml
- http://www.debian.org/security/2008/dsa-1554
