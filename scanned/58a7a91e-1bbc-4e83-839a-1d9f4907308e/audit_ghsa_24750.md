# [C] Remote Code Execution in Apache Struts

## Summary
Severity: Critical
Advisory: GHSA-pvm9-288c-v5wq
CVE: CVE-2016-3082
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pvm9-288c-v5wq
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.20.3
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.24 <2.3.24.3
- Maven: `org.apache.struts:struts2-core` — affected >=2.3.28 <2.3.28.1

## Details
XSLTResult allows for the location of a stylesheet being passed as a request parameter. In some circumstances this can be used to inject remotely executable code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3082
- https://github.com/apache/struts
- http://struts.apache.org/docs/s2-031.html
