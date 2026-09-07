# [M] OpenClaw safeBins file-existence oracle information disclosure

## Summary
Severity: Medium
Advisory: GHSA-6c9j-x93c-rw6j
CVE: CVE-2026-4040
CWE: CWE-203
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-6c9j-x93c-rw6j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
An information disclosure vulnerability in OpenClaw's `tools.exec.safeBins` approval flow allowed a file-existence oracle.

When safe-bin validation examined candidate file paths, command allow/deny behavior could differ based on whether a path already existed on the host filesystem. An attacker could probe for file presence by comparing outcomes for existing vs non-existing filenames.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Latest published vulnerable version at triage time: `2026.2.17`
- Planned patched version: `2026.2.18`

## Impact
Attackers with access to this execution surface could infer whether specific files exist (for example secrets/config files), enabling filesystem enumeration and improving follow-on attack planning.

## Fix
The safe-bin policy was changed to deterministic argv-only validation without host file-existence checks. File-oriented flags are blocked for safe-bin mode (for example `sort -o`, `jq -f`, `grep -f`), and trusted-path checks remain enforced.

## Fix Commit(s)
- `bafdbb6f112409a65decd3d4e7350fbd637c7754`

Found using [MCPwner](https://github.com/Pigyon/MCPwner)

Thanks @nedlir for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6c9j-x93c-rw6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-4040
- https://github.com/openclaw/openclaw/commit/bafdbb6f112409a65decd3d4e7350fbd637c7754
- https://github.com/openclaw/openclaw
