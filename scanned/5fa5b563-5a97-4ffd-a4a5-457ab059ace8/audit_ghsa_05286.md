# [M] Apache CXF has Authentication Bypass in OAuth2 TokenIntrospectionService

## Summary
Severity: Medium
Advisory: GHSA-542g-m3fx-q86f
CVE: CVE-2026-50623
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-542g-m3fx-q86f
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
An authentication bypass vulnerability exists in the OAuth2 TokenIntrospectionService in Apache CXF. Due to a missing 'throw' keyword in the security context check, the introspection endpoint (/services/oauth2/introspect) can be accessed by any unauthenticated network attacker. However note that this is a safeguard only in the case that someone forgot to enable authentication on the service. Users are recommended to upgrade to version 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50623
- https://github.com/apache/cxf
- https://lists.apache.org/thread/ydzj8m5mqmjy13xgyj9mkk9hfff63qq7
- http://www.openwall.com/lists/oss-security/2026/06/11/3
