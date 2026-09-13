# [M] OpenClaw's system.run approval TOCTOU via mutable symlink cwd target on node host

## Summary
Severity: Medium
Advisory: GHSA-mwcg-wfq3-4gjc
CVE: CVE-2026-32043
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-mwcg-wfq3-4gjc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
In `openclaw@2026.2.24`, approval-bound `system.run` on node hosts could be influenced by mutable symlink `cwd` targets between approval and execution.

### Details
Approval matching on the gateway validated command/argv and binding fields, including `cwd`, as provided text. Node execution later used runtime `cwd` resolution. A symlinked `cwd` could therefore be retargeted after approval and before spawn.

OpenClaw's trust model does not treat one shared gateway as a multi-tenant adversarial boundary, but approval integrity is still a security boundary for operator-reviewed command execution.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.24`
- Patched: `>= 2026.2.25` 

### Fix Commit(s)
- `f789f880c934caa8be25b38832f27f90f37903db`

### Remediation
The fix adds defense-in-depth hardening for approval-bound node execution:
- reject symlink `cwd` paths for approval-bound `system.run`
- canonicalize path-like executable argv before spawn
- bind CLI approval requests to exact `commandArgv`

### Release Process Note
Patched version is pre-set to the release (`2026.2.25`). Advisory published with npm release `2026.2.25`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mwcg-wfq3-4gjc
- https://nvd.nist.gov/vuln/detail/CVE-2026-32043
- https://github.com/openclaw/openclaw/commit/f789f880c934caa8be25b38832f27f90f37903db
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-time-of-check-time-of-use-via-mutable-symlink-in-system-run-cwd-parameter
