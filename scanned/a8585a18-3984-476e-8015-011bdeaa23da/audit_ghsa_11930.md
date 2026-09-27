# [H] OpenClaw has Windows system.run approval mismatch on cmd.exe /c trailing arguments

## Summary
Severity: High
Advisory: GHSA-5v6x-rfc3-7qfr
CVE: CVE-2026-22168
CWE: CWE-863, CWE-88
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-5v6x-rfc3-7qfr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
A Windows `system.run` approval-integrity mismatch in the `cmd.exe /c` path could allow trailing arguments to execute while approval/audit text reflected only a benign command string.

This requires an authenticated operator context using the approvals flow and a trusted Windows node.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published vulnerable version (as of 2026-02-21): `2026.2.19-2`
- Vulnerable range: `<=2026.2.19-2`
- Patched version (planned next release): `2026.2.21`

### Attack Scenario
1. An authenticated operator approval is created for a benign command text (for example, `echo`).
2. A `system.run` request uses `cmd.exe /c` with extra trailing arguments.
3. Prior behavior could bind approval/audit text to the benign command while still executing the full argument tail on the node.

### Impact
- Local command execution on the trusted Windows node process account.
- Approval/audit command text integrity mismatch.

### Fix
- Canonicalize the full command tail after `cmd.exe /c`.
- Reuse one shared command canonicalization/validation path for validation, approval matching, and execution/audit text.
- Add regression coverage for trailing-argument smuggling and approval binding.

### Fix Commit(s)
- `6007941f04df1edcca679dd6c95949744fdbd4df`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.21`). Once that npm release is live, this advisory can be published directly.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5v6x-rfc3-7qfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-22168
- https://github.com/openclaw/openclaw/commit/6007941f04df1edcca679dd6c95949744fdbd4df
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-command-injection-via-cmd-exe-c-trailing-arguments-in-system-run
