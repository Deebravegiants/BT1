# [C] Expression Language Injection in Apache Syncope

## Summary
Severity: Critical
Advisory: GHSA-vjqw-r3ww-wj2w
CVE: CVE-2020-1959
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-vjqw-r3ww-wj2w
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope-core` — affected >=0 <2.1.6

## Details
A Server-Side Template Injection was identified in Apache Syncope prior to 2.1.6 enabling attackers to inject arbitrary Java EL expressions, leading to an unauthenticated Remote Code Execution (RCE) vulnerability. Apache Syncope uses Java Bean Validation (JSR 380) custom constraint validators. When building custom constraint violation error messages, they support different types of interpolation, including Java EL expressions. Therefore, if an attacker can inject arbitrary data in the error message template being passed, they will be able to run arbitrary Java code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1959
- http://syncope.apache.org/security
