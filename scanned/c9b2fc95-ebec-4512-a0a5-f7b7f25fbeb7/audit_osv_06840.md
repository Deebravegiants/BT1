# [H] WAF bypass of the ModSecurity v3 release line

## Summary
Severity: High
Advisory: BIT-modsecurity-2024-1019
Aliases: BIT-modsecurity2-2024-1019, CVE-2024-1019
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-modsecurity-2024-1019
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=3.0.0 <3.0.12

## Details
ModSecurity / libModSecurity 3.0.0 to 3.0.11 is affected by a WAF bypass for path-based payloads submitted via specially crafted request URLs. ModSecurity v3 decodes percent-encoded characters present in request URLs before it separates the URL path component from the optional query string component. This results in an impedance mismatch versus RFC compliant back-end applications. The vulnerability hides an attack payload in the path component of the URL from WAF rules inspecting it. A back-end may be vulnerable if it uses the path component of request URLs to construct queries. Integrators and users are advised to upgrade to 3.0.12. The ModSecurity v2 release line is not affected by this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/34KDQNZE2RS3CWFG5654LNHKXXDPIW5I/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/K6ZGABPJK2JPVH2JDFHZ5LQLWGONUH7V/
- https://owasp.org/www-project-modsecurity/tab_cves#cve-2024-1019-2024-01-30
- https://nvd.nist.gov/vuln/detail/CVE-2024-1019
