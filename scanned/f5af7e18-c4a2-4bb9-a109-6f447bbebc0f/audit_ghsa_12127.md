# [M] OpenClaw: Bonjour/DNS-SD TXT metadata steers CLI routing after failed service resolution

## Summary
Severity: Medium
Advisory: GHSA-rvqr-hrcc-j9vv
CVE: CVE-2026-35659
CWE: CWE-345, CWE-642
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-rvqr-hrcc-j9vv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Bonjour and DNS-SD TXT metadata could still steer CLI routing even when actual service resolution failed, allowing unresolved hints to influence the chosen target.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `deecf68b59a9b7eea978e40fd3c2fe543087b569`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/infra/bonjour-discovery.ts now resolves and returns only concrete endpoints instead of falling back to unresolved TXT host and port hints.
- src/cli/gateway-cli/discover.ts consumes only the fail-closed resolved endpoint path.

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rvqr-hrcc-j9vv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35659
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/deecf68b59a9b7eea978e40fd3c2fe543087b569
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unresolved-service-metadata-routing-via-bonjour-and-dns-sd-discovery
