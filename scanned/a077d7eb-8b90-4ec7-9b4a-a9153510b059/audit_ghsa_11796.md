# [H] OpenClaw: Unrecognized script runners could bypass `system.run` approval integrity

## Summary
Severity: High
Advisory: GHSA-qc36-x95h-7j53
CVE: CVE-2026-32978
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-qc36-x95h-7j53
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, node-host `system.run` approvals did not bind a mutable file operand for some script runners, including forms such as `tsx` and `jiti`. An attacker could obtain approval for a benign script-runner command, rewrite the referenced script on disk, and have the modified code execute under the already approved run context.

## Impact
Deployments that rely on node-host `system.run` approvals for script integrity could execute rewritten local code after operator approval. This can lead to unintended local code execution as the OpenClaw runtime user.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `< 2026.3.11`
- Fixed in: `2026.3.11`

## Technical Details
The approval planner only tracked mutable script operands for a hardcoded set of interpreters and runtime forms. Commands such as `tsx ./run.ts` and `jiti ./run.ts` fell through without a bound file snapshot, so the final pre-execution revalidation step was skipped.

## Fix
OpenClaw now fails closed for approval-backed interpreter and runtime commands unless it can bind exactly one concrete local file operand, and it extends direct-file binding coverage for additional runtime forms. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qc36-x95h-7j53
- https://nvd.nist.gov/vuln/detail/CVE-2026-32978
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-approval-bypass-via-unrecognized-script-runners
