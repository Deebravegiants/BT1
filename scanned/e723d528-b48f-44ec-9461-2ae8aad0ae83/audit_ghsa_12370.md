# [M] JLine vulnerable to out of memory error

## Summary
Severity: Medium
Advisory: GHSA-2268-98wh-qfhf
CVE: CVE-2023-50572
CWE: CWE-122, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-29
Source: https://github.com/advisories/GHSA-2268-98wh-qfhf
Type: github-advisory

## Affected
- Maven: `org.jline:jline-parent` — affected >=0 <3.25.0

## Details
An issue in the component `GroovyEngine.execute` of JLine v3.24.1 allows attackers to cause an out of memory (OOM) error exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50572
- https://github.com/jline/jline3/issues/909
- https://github.com/jline/jline3/commit/f3c60a3e6255e8e0c20d5043a4fe248446f292bb
- https://github.com/jline/jline3
