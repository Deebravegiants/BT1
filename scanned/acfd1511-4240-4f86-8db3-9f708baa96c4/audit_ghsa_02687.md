# [H] Directory traversal in Eclipse Mojarra

## Summary
Severity: High
Advisory: GHSA-rpq8-mmwh-q9hm
CVE: CVE-2020-6950
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-rpq8-mmwh-q9hm
Type: github-advisory

## Affected
- Maven: `org.glassfish:mojarra-parent` — affected >=0 <2.3.14

## Details
Directory traversal in Eclipse Mojarra before 2.3.14 allows attackers to read arbitrary files via the loc parameter or con parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-6950
- https://github.com/eclipse-ee4j/mojarra/issues/4571
- https://github.com/eclipse-ee4j/mojarra/commit/cefbb9447e7be560e59da2da6bd7cb93776f7741
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=550943
- https://github.com/eclipse-ee4j/mojarra
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
