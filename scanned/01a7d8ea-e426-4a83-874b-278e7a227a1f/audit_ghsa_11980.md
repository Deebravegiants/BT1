# [M] OpenClaw has a Trusted-proxy Control UI pairing bypass which allows unpaired node sessions

## Summary
Severity: Medium
Advisory: GHSA-vvgp-4c28-m3jm
CVE: CVE-2026-32057
CWE: CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vvgp-4c28-m3jm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
## Summary
A trusted-proxy Control UI pairing bypass accepted `client.id=control-ui` without device identity checks. The bypass did not require `operator` role, so an authenticated `node` role session could connect unpaired and reach node event methods.

## Impact
With trusted-proxy authentication enabled, a `node` role websocket client could skip pairing by using `client.id=control-ui`. That created an authorization boundary bypass from a node-scoped connection into node event execution flows.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected range: `<= 2026.2.24`
- Latest published vulnerable version: `2026.2.24`
- Patched in next release: `2026.2.25` (pre-set below so this advisory is ready to publish after npm release)

## Fix
The trusted-proxy Control UI bypass now additionally requires `role === "operator"`.

### Fix Commit(s)
- `ec45c317f5d0631a3d333b236da58c4749ede2a3`

## Release Process Note
`patched_versions` is intentionally pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.2.25` is published, the remaining GHSA action is to publish this advisory.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vvgp-4c28-m3jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32057
- https://github.com/openclaw/openclaw/commit/ec45c317f5d0631a3d333b236da58c4749ede2a3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-control-ui-client-id-parameter
