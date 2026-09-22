# [H] TerriaJS-Server has a domain validation bypass vulnerability in its proxy allowlist

## Summary
Severity: High
Advisory: GHSA-w789-49fc-v8hr
CVE: CVE-2026-27818
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-w789-49fc-v8hr
Type: github-advisory

## Affected
- npm: `terriajs-server` — affected >=0 <4.0.3

## Details
### Impact
A validation bug allows an attacker to proxy domains not explicitly allowed in the `proxyableDomains` configuration.

The validation only checks if a hostname _ended_ with an allowed domain. This meant:

If `example.com` is allowed in `proxyableDomains`:

- ✅ example.com is allowed (correct)
- ✅ api.example.com is allowed (correct)
- ⚠️ maliciousexample.com is allowed (incorrect)

An attacker could register maliciousexample.com and proxy content through `terriajs-server`, bypassing proxy restrictions.

### Patches
All versions up to 4.0.2 are affected. Upgrade to 4.0.3 to address the vulnerability.

## References
- https://github.com/TerriaJS/terriajs-server/security/advisories/GHSA-w789-49fc-v8hr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27818
- https://github.com/TerriaJS/terriajs-server/commit/3aaa5d9717162b245ae4569232bbe7d8673c913f
- https://github.com/TerriaJS/terriajs-server
- https://github.com/TerriaJS/terriajs-server/releases/tag/4.0.3
