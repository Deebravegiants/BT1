# [H] Apache James vulnerable to buffering attack

## Summary
Severity: High
Advisory: GHSA-w45j-f5g5-w94x
CVE: CVE-2022-28220
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-09
Source: https://github.com/advisories/GHSA-w45j-f5g5-w94x
Type: github-advisory

## Affected
- Maven: `org.apache.james:james-server` — affected >=0 <3.6.3
- Maven: `org.apache.james:james-server` — affected >=3.7.0 <3.7.1

## Details
Apache James prior to release 3.6.3 and 3.7.1 is vulnerable to a buffering attack relying on the use of the STARTTLS command. Fix of CVE-2021-38542, which solved similar problem fron Apache James 3.6.1, is subject to a parser differential and do not take into account concurrent requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28220
- https://github.com/apache/james-project
- https://james.apache.org/james/update/2022/08/26/james-3.7.1.html
- http://www.openwall.com/lists/oss-security/2022/09/20/1
