# [M] OpenClaw's exec allow-always can be bypassed via unrecognized multiplexer shell wrappers (busybox/toybox sh -c)

## Summary
Severity: Medium
Advisory: GHSA-gwqp-86q6-w47g
CVE: CVE-2026-22175
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-gwqp-86q6-w47g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
OpenClaw exec approvals could be bypassed in `allowlist` mode when `allow-always` was granted through unrecognized multiplexer shell wrappers (notably `busybox sh -c` and `toybox sh -c`).

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.22-2`
- Latest published vulnerable version at triage time: `2026.2.22-2` (checked on February 24, 2026)
- Fixed on `main`: yes
- Patched release: `2026.2.23`

### Details
Wrapper analysis treated `busybox`/`toybox` invocations as non-wrapper commands in this path, so `allow-always` persisted the wrapper binary path instead of the inner executable. That allowed later arbitrary payloads under the same multiplexer wrapper to satisfy the stored allowlist rule.

The fix hardens wrapper detection and persistence behavior for these multiplexer shell applets so approvals bind to intended inner executables and fail closed when unwrap safety is uncertain.

### Fix Commit(s)
- `a67689a7e3ad494b6637c76235a664322d526f9e`

### Release Process Note
`patched_versions` is pre-set to the released version (`2026.2.23`). This advisory now reflects released fix version `2026.2.23`.

OpenClaw thanks @jiseoung for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gwqp-86q6-w47g
- https://github.com/openclaw/openclaw/commit/a67689a7e3ad494b6637c76235a664322d526f9e
- https://github.com/openclaw/openclaw
