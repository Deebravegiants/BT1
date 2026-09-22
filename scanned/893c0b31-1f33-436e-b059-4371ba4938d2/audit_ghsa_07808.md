# [H] OpenClaw has a SSRF guard bypass via full-form IPv4-mapped IPv6 (loopback / metadata reachable)

## Summary
Severity: High
Advisory: GHSA-jrvc-8ff5-2f9f
CVE: CVE-2026-26324
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-jrvc-8ff5-2f9f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary

OpenClaw's SSRF protection could be bypassed using full-form IPv4-mapped IPv6 literals such as `0:0:0:0:0:ffff:7f00:1` (which is `127.0.0.1`). This could allow requests that should be blocked (loopback / private network / link-local metadata) to pass the SSRF guard.

- Vulnerable component: SSRF guard (`src/infra/net/ssrf.ts`)
- Issue type: SSRF protection bypass

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Vulnerable: `<= 2026.2.13`
- Patched: `>= 2026.2.14` (planned next release)

### Details

The SSRF guard's IP classification did not consistently detect private IPv4 addresses when they were embedded in IPv6 using full-form IPv4-mapped IPv6 notation. As a result, inputs like `0:0:0:0:0:ffff:7f00:1` could bypass loopback/private network blocking.

### Fix Commit(s)

- `c0c0e0f9aecb913e738742f73e091f2f72d39a19`

### Release Process Note

This advisory is kept in draft state with the patched version set to the planned next release. Once `openclaw@2026.2.14` is published to npm, the only remaining step should be to publish this advisory.

Thanks @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jrvc-8ff5-2f9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-26324
- https://github.com/openclaw/openclaw/commit/c0c0e0f9aecb913e738742f73e091f2f72d39a19
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
