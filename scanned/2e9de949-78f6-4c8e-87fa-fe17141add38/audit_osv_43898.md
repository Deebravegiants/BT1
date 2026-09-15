# [M] ArcadeDB before 26.8.1 SSRF via IMPORT DATABASE validator bypass

## Summary
Severity: Medium
Advisory: CVE-2026-75844
Aliases: GHSA-4w2m-77c8-83mw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75844
Type: osv

## Details
ArcadeDB versions before 26.8.1 contain a server-side request forgery vulnerability in the IMPORT DATABASE command where the security validator resolves and checks hostnames but the subsequent connection re-resolves the raw URL and follows redirects. Authenticated attackers can bypass the validator using DNS rebinding or HTTP redirects to access cloud metadata endpoints, internal services, or read arbitrary local files on default installations.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-4w2m-77c8-83mw
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75844.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75844
- https://www.vulncheck.com/advisories/arcadedb-before-ssrf-via-import-database-validator-bypass
