# [C] Spring Security OAuth2 Authorization Server: Insufficient validation of Dynamic Client Registration metadata

## Summary
Severity: Critical
Advisory: CVE-2026-59354
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-59354
Type: osv

## Details
In versions of Spring Security's OAuth2 Authorization Server module 7.0.0 through 7.0.4, when Dynamic Client Registration is explicitly enabled, the registration endpoint performs insufficient validation of certain client metadata fields supplied by the registering client. An attacker who possesses a valid Initial Access Token can register a malicious client with crafted metadata, which, depending on server configuration and how the metadata is later rendered or used, may result in Stored Cross-Site Scripting (XSS), Privilege Escalation, or Server-Side Request Forgery (SSRF).

## References
- https://repo.maven.apache.org/maven2/org/springframework/security/spring-security-oauth2-authorization-server/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59354.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59354
- https://spring.io/security/cve-2026-59354
- https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N&version=3.1
