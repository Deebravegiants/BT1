# [C] SSRF vulnerability using the Aegis DataBinding in Apache CXF

## Summary
Severity: Critical
Advisory: GHSA-qmgx-j96g-4428
CVE: CVE-2024-28752
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-qmgx-j96g-4428
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-databinding-aegis` — affected >=0 <3.5.8
- Maven: `org.apache.cxf:cxf-rt-databinding-aegis` — affected >=3.6.0 <3.6.3
- Maven: `org.apache.cxf:cxf-rt-databinding-aegis` — affected >=4.0.0 <4.0.4

## Details
A SSRF vulnerability using the Aegis DataBinding in versions of Apache CXF before 4.0.4, 3.6.3 and 3.5.8 allows an attacker to perform SSRF style attacks on webservices that take at least one parameter of any type. Users of other data bindings (including the default databinding) are not impacted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-28752
- https://github.com/apache/cxf/commit/d0baeb3ee64c6d7c883bd2f5c4cb0de6b0b5f463
- https://cxf.apache.org/security-advisories.data/CVE-2024-28752.txt
- https://github.com/apache/cxf
- https://security.netapp.com/advisory/ntap-20240517-0001
- http://www.openwall.com/lists/oss-security/2024/03/14/3
