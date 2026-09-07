# [M] OpenClaw's dispatch-wrapper depth-cap mismatch can bypass shell-wrapper approval gating in system.run allowlist mode

## Summary
Severity: Medium
Advisory: GHSA-ccg8-46r6-9qgj
CVE: CVE-2026-32023
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-ccg8-46r6-9qgj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
A wrapper-depth parsing mismatch in `system.run` allowed nested transparent dispatch wrappers (for example repeated `/usr/bin/env`) to suppress shell-wrapper detection while still matching allowlist resolution. In `security=allowlist` + `ask=on-miss`, this could bypass the expected approval prompt for shell execution.

### Severity / Trust Model
OpenClaw’s documented model treats authenticated gateway callers as trusted operators and exec approvals as operator guardrails. This issue is still a real approval-boundary bypass and is triaged as **Medium** in that model.

### Technical Details
- Dispatch-wrapper unwrapping stopped at `MAX_DISPATCH_WRAPPER_DEPTH`.
- Shell-wrapper extraction could return non-wrapper once depth was exhausted.
- Allowlist resolution could still succeed on partially unwrapped argv beginning with `/usr/bin/env`.
- Result: nested wrapper chains could execute `/bin/sh -c ...` without fresh approval in `allowlist` + `ask=on-miss`.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version at triage time: `2026.2.23`
- Vulnerable versions: `<= 2026.2.23`
- Patched versions (planned next release): `>= 2026.2.24`

### Fix Commit(s)
- `57c9a18180c8b14885bbd95474cbb17ff2d03f0b`

### Verification
- Added regression coverage for depth-overflow wrapper chains at resolution and `system.run` invocation layers.
- Reproduced previous PoC behavior before fix, then confirmed denial after fix with `SYSTEM_RUN_DENIED: approval required`.

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.24`) so once npm publish is complete, advisory publication can proceed without additional version edits.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ccg8-46r6-9qgj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32023
- https://github.com/openclaw/openclaw/commit/57c9a18180c8b14885bbd95474cbb17ff2d03f0b
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-approval-gating-bypass-via-dispatch-wrapper-depth-cap-mismatch-in-system-run
