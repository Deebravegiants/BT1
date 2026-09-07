# [M] Apache Struts Multiple XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-5pgj-r7c6-7c7w
CVE: CVE-2011-2087
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5pgj-r7c6-7c7w
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-parent` — affected >=0 <2.2.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in component handlers in the javatemplates (aka Java Templates) plugin in Apache Struts 2.x before 2.2.3 allow remote attackers to inject arbitrary web script or HTML via an arbitrary parameter value to a `.action` URI, related to improper handling of value attributes in 
1. `FileHandler.java`
1. `HiddenHandler.java`
1. `PasswordHandler.java`
1. `RadioHandler.java`
1. `ResetHandler.java`
1. `SelectHandler.java`
1. `SubmitHandler.java`
1. `TextFieldHandler.java`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2087
- https://github.com/apache/struts/commit/1736b56db702c6639a6d5ae1146dba5a262e3344
- https://github.com/apache/struts
- https://issues.apache.org/jira/browse/WW-3597
- https://issues.apache.org/jira/browse/WW-3608
- http://struts.apache.org/2.2.3/docs/version-notes-223.html
