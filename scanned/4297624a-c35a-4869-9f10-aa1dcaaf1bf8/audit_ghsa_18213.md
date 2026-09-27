# [H] Hono's flaw in URL path parsing could cause path confusion

## Summary
Severity: High
Advisory: GHSA-9hp6-4448-45g2
CVE: CVE-2025-58362
CWE: CWE-706
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-9hp6-4448-45g2
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.8.0 <4.9.6

## Details
### Summary

A flaw in the `getPath` utility function could allow path confusion and potential bypass of proxy-level ACLs (e.g. Nginx location blocks).

### Details

The original implementation relied on fixed character offsets when parsing request URLs. Under certain malformed absolute-form Request-URIs, this could lead to incorrect path extraction.

Most standards-compliant runtimes and reverse proxies reject such malformed requests with a 400 Bad Request, so the impact depends on the application and environment.

### Impact

If proxy ACLs are used to protect sensitive endpoints such as `/admin`, this flaw could have allowed unauthorized access. The confidentiality impact depends on what data is exposed: if sensitive administrative data is exposed, the impact may be High (CVSS 7.5); otherwise it may be Medium (CVSS 5.3).

### Resolution

The implementation has been updated to correctly locate the first slash after "://", preventing such path confusion.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-9hp6-4448-45g2
- https://nvd.nist.gov/vuln/detail/CVE-2025-58362
- https://github.com/honojs/hono/commit/1d79aedc3f82d8c9969b115fe61bc4bd705ec8de
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.9.6
