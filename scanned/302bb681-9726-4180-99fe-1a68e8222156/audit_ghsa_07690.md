# [M] OpenClaw's Chrome extension relay binds publicly due to wildcard treated as loopback

## Summary
Severity: Medium
Advisory: GHSA-qw99-grcx-4pvm
CVE: CVE-2026-28395
CWE: CWE-1327, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-qw99-grcx-4pvm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.14-1 <2026.2.12

## Details
## Summary
The Chrome extension relay (`ensureChromeExtensionRelayServer`) previously treated wildcard hosts (`0.0.0.0` / `::`) as loopback, which could make it bind the relay HTTP/WS server to all interfaces when a wildcard `cdpUrl` was passed.

## Impact
If configured with a wildcard `cdpUrl`, relay HTTP endpoints could become reachable off-host, leaking service presence/port and enabling DoS/brute-force traffic against the relay token header.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `>= 2026.1.14-1 < 2026.2.12`

## Fixed Versions
- Patched: `>= 2026.2.12` (released 2026-02-13)

## Fix Commit(s)
- 8d75a496bf5aaab1755c56cf48502d967c75a1d0

## Notes
- Earlier hardening for `/json*` auth and `/cdp` token checks landed in:
  - a1e89afcc19efd641c02b24d66d689f181ae2b5c

Thanks @qi-scape for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qw99-grcx-4pvm
- https://nvd.nist.gov/vuln/detail/CVE-2026-28395
- https://github.com/openclaw/openclaw/commit/8d75a496bf5aaab1755c56cf48502d967c75a1d0
- https://github.com/openclaw/openclaw/commit/a1e89afcc19efd641c02b24d66d689f181ae2b5c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://www.vulncheck.com/advisories/openclaw-unintended-public-binding-of-chrome-extension-relay-via-wildcard-cdpurl
