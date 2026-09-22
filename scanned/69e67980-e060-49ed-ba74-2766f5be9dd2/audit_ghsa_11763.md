# [M] OpenClaw exec allowlist safeBins short-option bypass could permit arbitrary file write

## Summary
Severity: Medium
Advisory: GHSA-3x3x-h76w-hp98
CVE: CVE-2026-32017
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-3x3x-h76w-hp98
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
### Summary
OpenClaw `exec` allowlist/safeBins policy could be bypassed with attached short-option payloads (for example `sort -o/tmp/poc`), enabling file-write operations while still satisfying safeBins checks.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Latest published vulnerable version: `2026.2.17`
- Patched in: `2026.2.19`

### Impact
When `tools.exec.security=allowlist` and `tools.exec.safeBins` included affected binaries, attached short-option payloads could bypass safeBins argument validation and permit file-write behavior that should have been denied.

### Fix Commit(s)
- cfe8457a0f4aae5324daec261d3b0aad1461a4bc
- bafdbb6f112409a65decd3d4e7350fbd637c7754
- fec48a5006eab37c6a5821726ccaeec886486b13

OpenClaw thanks @FailButWin and @Redgrave961 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3x3x-h76w-hp98
- https://nvd.nist.gov/vuln/detail/CVE-2026-32017
- https://github.com/openclaw/openclaw/commit/bafdbb6f112409a65decd3d4e7350fbd637c7754
- https://github.com/openclaw/openclaw/commit/cfe8457a0f4aae5324daec261d3b0aad1461a4bc
- https://github.com/openclaw/openclaw/commit/fec48a5006eab37c6a5821726ccaeec886486b13
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-write-via-short-option-bypass-in-exec-allowlist
