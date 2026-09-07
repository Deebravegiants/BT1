# [M] Apache James MIME4J improper input validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-jw7r-rxff-gv24
CVE: CVE-2024-21742
CWE: CWE-20, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-jw7r-rxff-gv24
Type: github-advisory

## Affected
- Maven: `org.apache.james:apache-mime4j-core` — affected >=0 <0.8.10

## Details
Improper input validation allows for header injection in MIME4J library when using MIME4J DOM for composing message.
This can be exploited by an attacker to add unintended headers to MIME messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21742
- https://github.com/apache/james-mime4j/commit/9dec5df2a588fed8027839815daefa79ee66efd1
- https://github.com/apache/james-mime4j/commit/d25fb3fd35db42b060789a20634fbe3cb84aba17
- https://github.com/apache/james-mime4j
- https://lists.apache.org/thread/nrqzg93219wdj056pqfszsd33dc54kfy
- http://www.openwall.com/lists/oss-security/2024/02/27/5
