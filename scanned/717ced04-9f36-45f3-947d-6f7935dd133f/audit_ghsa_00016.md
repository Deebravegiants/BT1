# [M] Cross site scripting in org.apache.nifi:nifi

## Summary
Severity: Medium
Advisory: GHSA-4qq9-rrq6-48ff
CVE: CVE-2018-17193
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-12-20
Source: https://github.com/advisories/GHSA-4qq9-rrq6-48ff
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=1.0.0 <1.8.0

## Details
The message-page.jsp error page used the value of the HTTP request header X-ProxyContextPath without sanitization, resulting in a reflected XSS attack. Mitigation: The fix to correctly parse and sanitize the request attribute value was applied on the Apache NiFi 1.8.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17193
- https://github.com/apache/nifi/commit/e62aa0252dfcf34dff0c3a9c51265b1d0f9dfc9f
- https://github.com/advisories/GHSA-4qq9-rrq6-48ff
- https://github.com/apache/nifi
- https://issues.apache.org/jira/browse/NIFI-5442
- https://nifi.apache.org/security.html#CVE-2018-17193
