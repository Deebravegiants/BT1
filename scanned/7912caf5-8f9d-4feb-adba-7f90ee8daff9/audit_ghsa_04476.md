# [M] Apache CXF OAuth2 HTTP Response Splitting via WWW-Authenticate Realm Injection

## Summary
Severity: Medium
Advisory: GHSA-xf62-wr5p-5p95
CVE: CVE-2026-50630
CWE: CWE-113
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-xf62-wr5p-5p95
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
A CRLF injection vulnerability exists in the OAuth2 AuthorizationUtils class. When constructing the WWW-Authenticate response header, the 'realm' parameter is concatenated without sanitizing Carriage Return (CR) and Line Feed (LF) characters. If an attacker can control the realm value, they can inject arbitrary HTTP headers or split the HTTP response entirely. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50630
- https://github.com/apache/cxf
- https://lists.apache.org/thread/bt7vnjzzkpd6vdhkxv103poor1jy5trm
- http://www.openwall.com/lists/oss-security/2026/06/11/7
