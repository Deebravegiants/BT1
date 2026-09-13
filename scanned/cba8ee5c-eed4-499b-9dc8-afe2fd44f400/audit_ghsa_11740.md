# [H] OpenClaw: Node system.run approval bypass via parent-symlink cwd rebind

## Summary
Severity: High
Advisory: GHSA-f7ww-2725-qvw2
CVE: CVE-2026-27545
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-f7ww-2725-qvw2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
## Summary
For `host=node` executions, approval context could be bypassed after approval-time by rebinding a writable parent symlink in `cwd` while preserving the visible `cwd` string.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.25`
- Fixed: `>= 2026.2.26` (planned next npm release)

## Impact
A command approved for one filesystem location could execute from a different location if a mutable parent symlink changed between approval and execution.

## Fix
- Added immutable approval-time plan preparation (`system.run.prepare`) and `systemRunPlanV2` canonical fields (`argv`, `cwd`, `agentId`, `sessionKey`).
- Enforced canonical plan values through approval request storage and forwarding-time sanitization.
- Rejected mutable parent-symlink path components during approval-plan building to block symlink rebind bypass.
- Follow-up refactors centralized command catalogs and approval context/error handling to reduce future drift.

## Fix Commit(s)
- `78a7ff2d50fb3bcef351571cb5a0f21430a340c1`
- `d82c042b09727a6148f3ca651b254c4a677aff26`
- `d06632ba45a8482192792c55d5ff0b2e21abb0a7`
- `4e690e09c746408b5e27617a20cb3fdc5190dbda`
- `4b4718c8dfce2e2c48404aa5088af7c013bed60b`

## Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.26`). Once npm `openclaw@2026.2.26` is published, publish this advisory directly without further version-field edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f7ww-2725-qvw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27545
- https://github.com/openclaw/openclaw/commit/4b4718c8dfce2e2c48404aa5088af7c013bed60b
- https://github.com/openclaw/openclaw/commit/4e690e09c746408b5e27617a20cb3fdc5190dbda
- https://github.com/openclaw/openclaw/commit/78a7ff2d50fb3bcef351571cb5a0f21430a340c1
- https://github.com/openclaw/openclaw/commit/d06632ba45a8482192792c55d5ff0b2e21abb0a7
- https://github.com/openclaw/openclaw/commit/d82c042b09727a6148f3ca651b254c4a677aff26
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-approval-bypass-via-parent-symlink-current-working-directory-rebind
