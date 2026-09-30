# [M] Apache Wicket: An attacker can intentionally trigger a memory leak

## Summary
Severity: Medium
Advisory: GHSA-9cxr-76pm-j3wf
CVE: CVE-2024-53299
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-23
Source: https://github.com/advisories/GHSA-9cxr-76pm-j3wf
Type: github-advisory

## Affected
- Maven: `org.apache.wicket:wicket-core` — affected >=7.0.0 <8.17.0
- Maven: `org.apache.wicket:wicket-core` — affected >=10.0.0 <10.3.0
- Maven: `org.apache.wicket:wicket-core` — affected >=9.0.0-M1 <9.19.0

## Details
The request handling in the core in Apache Wicket 7.0.0 on any platform allows an attacker to create a DOS via multiple requests to server resources.
Users are recommended to upgrade to versions 9.19.0 or 10.3.0, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53299
- https://github.com/apache/wicket
- https://lists.apache.org/thread/gyp2ht00c62827y0379lxh5dbx3hhho5
- https://wicket.apache.org/news/2025/01/31/wicket-8.17.0-released.html
- http://www.openwall.com/lists/oss-security/2025/01/22/12
