# [H] OpenClaw: system.run approvals did not bind PATH-token executable identity, enabling post-approval executable rebind

## Summary
Severity: High
Advisory: GHSA-q399-23r3-hfx4
CVE: CVE-2026-31997
CWE: CWE-367, CWE-426
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-q399-23r3-hfx4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
For `host=node` runs, approvals validated command context but did not pin executable identity for non-path-like `argv[0]` tokens (for example `tr`). If PATH resolution changed after approval, execution could run a different binary.

### Impact
A previously approved action could execute a different executable than the operator approved.

### Fix
Node `system.run` approvals now require immutable `systemRunPlan` data, and path-token commands are pinned to canonical executable identity (`realpath`) across approval and execution.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q399-23r3-hfx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-31997
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-executable-rebind-via-unbound-path-token-in-system-run-approvals
