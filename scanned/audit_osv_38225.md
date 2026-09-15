# [H] Directus has a SSRF Protection Bypass via IPv4-Mapped IPv6 Addresses in File Import

## Summary
Severity: High
Advisory: CVE-2026-35409
Aliases: GHSA-wv3h-5fx7-966h
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35409
Type: osv

## Details
Directus is a real-time API and App dashboard for managing SQL database content. Prior to 11.16.0, a Server-Side Request Forgery (SSRF) protection bypass has been identified and fixed in Directus. The IP address validation mechanism used to block requests to local and private networks could be circumvented using IPv4-Mapped IPv6 address notation. This vulnerability is fixed in 11.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35409.json
- https://github.com/directus/directus/security/advisories/GHSA-wv3h-5fx7-966h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35409
