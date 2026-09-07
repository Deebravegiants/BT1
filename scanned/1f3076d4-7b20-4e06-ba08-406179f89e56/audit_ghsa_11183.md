# [H] OpenClaw's authorization mismatch allowed write-scope agent runs to reach owner-only tools

## Summary
Severity: High
Advisory: GHSA-jr6x-2q95-fh2g
CWE: CWE-269, CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-jr6x-2q95-fh2g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
An authorization mismatch allowed authenticated callers with `operator.write` access to invoke owner-only tool surfaces (`gateway`, `cron`) through `agent` runs in scoped-token deployments.

### Impact
On affected deployments, write-scoped callers could perform control-plane actions beyond intended write scope.

### Fix
Owner-only gating is now enforced consistently for owner-only tool surfaces during agent execution, and tool scope classification was tightened to remove the privilege mismatch.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jr6x-2q95-fh2g
- https://github.com/openclaw/openclaw
