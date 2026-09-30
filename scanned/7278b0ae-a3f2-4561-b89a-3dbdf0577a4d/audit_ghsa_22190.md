# [M] Apache Struts2 Broken Access Control Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q5q8-jghf-3pm3
CVE: CVE-2013-4310
CWE: CWE-284
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q5q8-jghf-3pm3
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.15.3

## Details
The Struts 2 action mapping mechanism supports the special parameter prefix action: which is intended to help with attaching navigational information to buttons within forms, under certain conditions this can be used to bypass security constraints. 

In Struts 2.3.15.3 the action mapping mechanism was changed to avoid circumventing security constraints. Two additional constants were introduced to steer behaviour of DefaultActionMapper:

- struts.mapper.action.prefix.enabled - when set to false support for "action:" prefix is disabled, set to false by default
- struts.mapper.action.prefix.crossNamespaces - when set to false, actions defined with "action:" prefix must be in the same namespace as current action

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4310
- https://github.com/apache/struts/commit/0c8366cb792227d484b9ca13e537037dd0cb57dc
- https://github.com/apache/struts
- http://struts.apache.org/release/2.3.x/docs/s2-018.html
