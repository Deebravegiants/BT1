# [H] Injection in Apache Syncope

## Summary
Severity: High
Advisory: GHSA-4w4p-xwrr-9crh
CVE: CVE-2020-1961
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-4w4p-xwrr-9crh
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=2.0.0 <2.0.15
- Maven: `org.apache.syncope:syncope-core` — affected >=2.1.0 <2.1.6

## Details
Vulnerability to Server-Side Template Injection on Mail templates for Apache Syncope 2.0.X releases prior to 2.0.15, 2.1.X releases prior to 2.1.6, enabling attackers to inject arbitrary JEXL expressions, leading to Remote Code Execution (RCE) was discovered.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1961
- http://syncope.apache.org/security
