# [M] OpenClaw's serialize sandbox registry writes to prevent races and delete-rollback corruption

## Summary
Severity: Medium
Advisory: GHSA-gq83-8q7q-9hfx
CVE: CVE-2026-32018
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-gq83-8q7q-9hfx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Impact

Concurrent `updateRegistry`/`removeRegistryEntry` operations for sandbox containers and browsers could lose updates or resurrect removed entries under race conditions.

The registry writes were read-modify-write in a window with no locking and permissive fallback parsing, so concurrent registry updates could produce stale snapshots and overwrite each other.

That desyncs sandbox state and can affect `sandbox list`, `sandbox prune`, and `sandbox recreate --all` behavior.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Patched versions: `2026.2.18`

## Fix Commit(s)

- `cc29be8c9`

OpenClaw thanks @kexinoh for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gq83-8q7q-9hfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32018
- https://github.com/openclaw/openclaw/commit/cc29be8c9
- https://github.com/openclaw/openclaw/commit/cc29be8c9bcdfaecb90f0ab13124c8f5362a6741
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-race-condition-in-sandbox-registry-write-operations
