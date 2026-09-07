# [M] Cross-site scripting in jfinal

## Summary
Severity: Medium
Advisory: GHSA-2c25-xfpq-8w9r
CVE: CVE-2021-33348
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-13
Source: https://github.com/advisories/GHSA-2c25-xfpq-8w9r
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0 <4.9.11

## Details
An issue was discovered in JFinal framework v4.9.10 and below. The "set" method of the "Controller" class of jfinal framework is not strictly filtered, which will lead to XSS vulnerabilities in some cases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33348
- https://github.com/jfinal/jfinal/issues/188
