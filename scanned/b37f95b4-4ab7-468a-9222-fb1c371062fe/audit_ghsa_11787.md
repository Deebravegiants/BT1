# [M] OpenClaw has Windows Lobster shell fallback command injection in constrained fallback path

## Summary
Severity: Medium
Advisory: GHSA-fg3m-vhrr-8gj6
CVE: CVE-2026-31995
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-fg3m-vhrr-8gj6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.21 <2026.2.19

## Details
### Summary
On Windows, the Lobster extension previously retried certain spawn failures (`ENOENT`/`EINVAL`) with `shell: true` for wrapper compatibility. In that fallback path, tool-provided arguments could be interpreted by `cmd.exe` if fallback was triggered.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version at triage: `2026.2.17`
- Affected range: `>= 2026.1.21 <= 2026.2.17`
- Patched version: `2026.2.19` (pre-set for next release)

### Fix
The Windows shell fallback was removed. Wrapper compatibility is preserved by resolving `.cmd`/`.bat` shims to a concrete Node entrypoint (or executable) and executing with explicit argv (no shell). If a safe entrypoint cannot be resolved, execution now fails closed with a guided error.

### Fix Commit(s)
- `ba7be018da354ea9f803ed356d20464df0437916`

### Severity Context
This issue requires Windows plus fallback-triggering conditions, and argument control through a local operator-defined workflow. 

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fg3m-vhrr-8gj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-31995
- https://github.com/openclaw/openclaw/commit/ba7be018da354ea9f803ed356d20464df0437916
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-command-injection-via-windows-shell-fallback-in-lobster-extension
