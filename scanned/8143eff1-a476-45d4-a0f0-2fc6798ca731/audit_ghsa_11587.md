# [M] OpenClaw has allowlist exec-guard bypass via env -S

## Summary
Severity: Medium
Advisory: GHSA-48wf-g7cp-gr3m
CVE: CVE-2026-31992
CWE: CWE-184, CWE-193
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-48wf-g7cp-gr3m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
In `allowlist` mode, `system.run` guardrails could be bypassed through `env -S`, causing policy-analysis/runtime-execution mismatch for shell wrapper payloads.

### Severity Rationale (Medium)
This issue is rated **medium** because it is a guardrail/policy bypass in OpenClaw's trusted-operator model, not an authentication boundary break.

- Authenticated Gateway callers are trusted operators by design.
- `exec` approvals/allowlists are operator safety controls.
- The bug still weakens expected safety behavior and can enable unintended command execution when untrusted content influences tool input.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.22-2`
- Patched versions: `>= 2026.2.23`

Latest published npm version checked during triage: `2026.2.22-2`.

### Technical Impact
When `/usr/bin/env` is allowlisted, `env -S 'sh -c ...'` could be treated as allowed non-wrapper argv while runtime still executes shell-wrapper semantics.

### Fix Commit(s)
- `a1c4bf07c6baad3ef87a0e710fe9aef127b1f606` (core allowlist/runtime parity hardening)
- `3f923e831364d83d0f23499ee49961de334cf58b` (explicit `env -S` regressions)

### Release Process Note
`patched_versions` is pre-set to `>= 2026.2.23`, so this advisory is now public.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-48wf-g7cp-gr3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-31992
- https://github.com/openclaw/openclaw/commit/3f923e831364d83d0f23499ee49961de334cf58b
- https://github.com/openclaw/openclaw/commit/a1c4bf07c6baad3ef87a0e710fe9aef127b1f606
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-exec-guard-bypass-via-env-s
