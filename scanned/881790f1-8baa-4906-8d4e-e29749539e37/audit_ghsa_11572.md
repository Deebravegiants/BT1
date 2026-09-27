# [M] In OpenClaw, manually adding sort to tools.exec.safeBins could bypass allowlist approval via --compress-program

## Summary
Severity: Medium
Advisory: GHSA-4gc7-qcvf-38wg
CVE: CVE-2026-32010
CWE: CWE-184, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-4gc7-qcvf-38wg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
This issue applies to a **non-default configuration** only.
If `sort` is manually added to `tools.exec.safeBins`, OpenClaw could treat `sort --compress-program=<prog>` as valid safe-bin usage.
In `security=allowlist` + `ask=on-miss`, this could satisfy allowlist checks and skip operator approval, while GNU `sort` may invoke an external program via `--compress-program`.

### Affected Packages / Versions
- Ecosystem: npm
- Package: `openclaw`
- Affected: `<= 2026.2.21-2`
- Patched (planned next release): `>= 2026.2.22`

### Default Installations
Default installs are not impacted by this specific path because `sort` is not included in default `tools.exec.safeBins`.

### Impact
- Type: approval/allowlist bypass in optional safe-bin configuration
- Scope: deployments that explicitly include `sort` in `tools.exec.safeBins` and use `allowlist + ask=on-miss`
- Consequence: an external program may run under the OpenClaw process context without expected approval

### Technical Details
- `sort` safe-bin profile allowed `--compress-program` as a value flag.
- Safe-bin satisfaction could therefore mark allowlist checks as satisfied.
- In `ask=on-miss`, satisfied allowlist checks skip approval prompts.

### Fix
- Block `--compress-program` in safe-bin sort policy.
- Add unit and e2e regression coverage for `sort --compress-program` denial in safe-bin mode.

### Fix Commit(s)
- `57fbbaebca4d34d17549accf6092ae26eb7b605c`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4gc7-qcvf-38wg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32010
- https://github.com/openclaw/openclaw/commit/57fbbaebca4d34d17549accf6092ae26eb7b605c
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-sort-compress-program-parameter
