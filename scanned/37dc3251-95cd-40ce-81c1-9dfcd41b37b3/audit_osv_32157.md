# [H] CVE-2025-25064

## Summary
Severity: High
Advisory: CVE-2025-25064
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-03
Source: https://osv.dev/vulnerability/CVE-2025-25064
Type: osv

## Details
SQL injection vulnerability in the ZimbraSync Service SOAP endpoint in Zimbra Collaboration 10.0.x before 10.0.12 and 10.1.x before 10.1.4 due to insufficient sanitization of a user-supplied parameter. Authenticated attackers can exploit this vulnerability by manipulating a specific parameter in the request, allowing them to inject arbitrary SQL queries that could retrieve email metadata.

## References
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.12#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.4#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25064.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25064
