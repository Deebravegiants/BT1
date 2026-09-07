# [M] OpenSymphony XWork vulnerable to improper input validation

## Summary
Severity: Medium
Advisory: GHSA-h7mf-qrm9-2848
CVE: CVE-2007-4556
CWE: CWE-20
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-h7mf-qrm9-2848
Type: github-advisory

## Affected
- Maven: `opensymphony:xwork` — affected >=0 <1.2.3
- Maven: `opensymphony:xwork` — affected >=2.0.0 <2.0.4

## Details
XWork is an command-pattern framework that is used to power WebWork as well as other applications. Struts support in OpenSymphony XWork before 1.2.3, and 2.x before 2.0.4, as used in WebWork and Apache Struts, recursively evaluates all input as an Object-Graph Navigation Language (OGNL) expression when altSyntax is enabled, which allows remote attackers to cause a denial of service (infinite loop) or execute arbitrary code via form input beginning with a "%{" sequence and ending with a "}" character. 

Note: Version 2.0.4 marks the change from `opensymphony:xwork` to `com.opensymphony:xwork`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-4556
- http://struts.apache.org/2.x/docs/s2-001.html
