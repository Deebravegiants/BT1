# [H] Apache HttpClient accepts SCRAM-SHA-256 authentication without proper mutual authentication verification

## Summary
Severity: High
Advisory: GHSA-v468-qcjx-r72w
CVE: CVE-2026-40542
CWE: CWE-304
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-v468-qcjx-r72w
Type: github-advisory

## Affected
- Maven: `org.apache.httpcomponents.client5:httpclient5` — affected >=5.6-alpha1 <5.6.1

## Details
Missing critical step in authentication in Apache HttpClient 5.6 allows an attacker to cause the client to accept SCRAM-SHA-256 authentication without proper mutual authentication verification. Users are recommended to upgrade to version 5.6.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40542
- https://github.com/apache/httpcomponents-client/commit/726eac2323d370435d8afca1e0540aa099927f18
- https://github.com/apache/httpcomponents-client
- https://lists.apache.org/thread/tfmgv86xr0z1y096vs3z0y315t1v3o97
- http://www.openwall.com/lists/oss-security/2026/04/22/5
