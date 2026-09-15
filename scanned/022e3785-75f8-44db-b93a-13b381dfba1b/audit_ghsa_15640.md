# [H] Apache Wicket: Remote code execution via XSLT injection

## Summary
Severity: High
Advisory: GHSA-hhwc-gh8h-9rrp
CVE: CVE-2024-36522
CWE: CWE-74
Ecosystem: Maven
Published: 2024-07-12
Source: https://github.com/advisories/GHSA-hhwc-gh8h-9rrp
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-util` — affected >=10.0.0-M1 <10.1.0
- Maven: `org.apache.wicket:wicket-util` — affected >=9.0.0 <9.18.0
- Maven: `org.apache.wicket:wicket-util` — affected >=8.0.0 <8.16.0

## Details
The default configuration of XSLTResourceStream.java is vulnerable to remote code execution via XSLT injection when processing input from an untrusted source without validation.
Users are recommended to upgrade to versions 10.1.0, 9.18.0 or 8.16.0, which fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36522
- https://github.com/apache/wicket
- https://lists.apache.org/thread/w613qh7yors840pbx00l1pq6wkl9jzkc
- http://www.openwall.com/lists/oss-security/2024/07/12/2
