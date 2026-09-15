# [M] OpenClaw's sandboxed sessions_spawn now enforces sandbox inheritance for cross-agent spawns

## Summary
Severity: Medium
Advisory: GHSA-p7gr-f84w-hqg5
CVE: CVE-2026-32048
CWE: CWE-269, CWE-284, CWE-732
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-p7gr-f84w-hqg5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
A sandboxed session could use cross-agent `sessions_spawn` to create a child under an agent configured with `sandbox.mode="off"`, downgrading runtime confinement.

### Impact
In mixed-agent setups that allow cross-agent spawning, a sandboxed requester could escape into an unsandboxed child runtime.

### Fix
Spawn-time sandbox inheritance is now enforced: if the requester is sandboxed and the resolved child runtime would be unsandboxed, spawn is rejected.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p7gr-f84w-hqg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32048
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-escape-via-cross-agent-sessions-spawn
