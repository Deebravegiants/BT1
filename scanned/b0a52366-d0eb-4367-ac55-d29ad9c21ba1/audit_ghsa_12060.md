# [M] Temporary path handling could write outside OpenClaw temp boundary

## Summary
Severity: Medium
Advisory: GHSA-33hm-cq8r-wc49
CVE: CVE-2026-32026
CWE: CWE-22, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-33hm-cq8r-wc49
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
Sandbox media local-path validation accepted absolute paths under host tmp, even when those paths were outside the active sandbox root.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version verified during triage: `2026.2.23`
- Affected versions: `<= 2026.2.23`
- Patched versions (planned next release): `>= 2026.2.24`

### Details
In affected versions, sandbox media path resolution allowed absolute host tmp paths as trusted media inputs when they were under `os.tmpdir()`, without requiring that the path stay within the active `sandboxRoot`.
Because outbound attachment hydration consumed these paths as already validated, this enabled out-of-sandbox host tmp file reads and exfiltration through attachment delivery.

### Impact
- Confidentiality impact: high for deployments relying on `sandboxRoot` as a strict local filesystem boundary.
- Practical impact: attacker-controlled media references could read and attach host tmp files outside the sandbox workspace boundary.

### Remediation
- Restrict sandbox tmp-path acceptance to OpenClaw-managed temp roots only.
- Default SDK/extension temp helpers to OpenClaw-managed temp roots.
- Add CI guardrails to prevent broad tmp-root regressions in messaging/channel code paths.

### Fix Commit(s)
- `d3da67c7a9b463edc1a9b1c1f7af107a34ca32f5`
- `79a7b3d22ef92e36a4031093d80a0acb0d82f351`
- `def993dbd843ff28f2b3bad5cc24603874ba9f1e`

### Release Process Note
The advisory is pre-set with patched version `2026.2.24` so it is ready for publication once that npm release is available.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-33hm-cq8r-wc49
- https://nvd.nist.gov/vuln/detail/CVE-2026-32026
- https://github.com/openclaw/openclaw/commit/79a7b3d22ef92e36a4031093d80a0acb0d82f351
- https://github.com/openclaw/openclaw/commit/d3da67c7a9b463edc1a9b1c1f7af107a34ca32f5
- https://github.com/openclaw/openclaw/commit/def993dbd843ff28f2b3bad5cc24603874ba9f1e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-improper-temporary-path-validation-in-sandbox
