# [M] Eclipse Parsson Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g8p6-p27c-52fx
CVE: CVE-2023-4043
CWE: CWE-20, CWE-834
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-03
Source: https://github.com/advisories/GHSA-g8p6-p27c-52fx
Type: github-advisory

## Affected
- Maven: `org.eclipse.parsson:project` — affected >=1.1.0 <1.1.4
- Maven: `org.eclipse.parsson:project` — affected >=0 <1.0.5

## Details
In Eclipse Parsson before versions 1.1.4 and 1.0.5, Parsing JSON from untrusted sources can lead malicious actors to exploit the fact that the built-in support for parsing numbers with large scale in Java has a number of edge cases where the input text of a number can lead to much larger processing time than one would expect.


To mitigate the risk, parsson put in place a size limit for the numbers as well as their scale.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4043
- https://github.com/eclipse-ee4j/parsson/pull/100
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/13
