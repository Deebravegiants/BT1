# [H] Apache CXF OAuth2 Log Injection via Unsanitized Client Identifier

## Summary
Severity: High
Advisory: GHSA-f8p7-h97q-7vx7
CVE: CVE-2026-50629
CWE: CWE-93
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-f8p7-h97q-7vx7
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
The 'clientId' parameter from incoming HTTP requests is directly concatenated into OAuth2 server log warning messages without sanitizing control characters. This allows an attacker to inject arbitrary content, including fake log entries, into the server's log files. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50629
- https://github.com/apache/cxf
- https://lists.apache.org/thread/xw95po30p8th58ms1no6b0f2375cql00
- http://www.openwall.com/lists/oss-security/2026/06/11/6
