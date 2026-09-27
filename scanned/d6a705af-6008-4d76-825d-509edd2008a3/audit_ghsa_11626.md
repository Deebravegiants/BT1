# [M] OpenClaw's system.run approvals did not bind mutable script operands across approval and execution

## Summary
Severity: Medium
Advisory: GHSA-8g75-q649-6pv6
CVE: CVE-2026-32921
CWE: CWE-285, CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-8g75-q649-6pv6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.8

## Details
OpenClaw's `system.run` approval flow did not bind mutable interpreter-style script operands across approval and execution.

A caller could obtain approval for an execution such as `sh ./script.sh`, rewrite the approved script before execution, and then execute different content under the previously approved command shape. The approved `argv` values remained the same, but the mutable script operand content could drift after approval.

Latest published npm version verified vulnerable: `2026.3.7`

The initial March 7, 2026 fix in `c76d29208bf6a7f058d2cf582519d28069e42240` added approval binding for shell scripts and a narrow interpreter set, but follow-up maintainer review on March 8, 2026 found that `bun` and `deno` script operands still did not produce `mutableFileOperand` snapshots.

A complete fix shipped on March 9, 2026 in `cf3a479bd1204f62eef7dd82b4aa328749ae6c91`, which binds approved `bun` and `deno run` script operands to on-disk file snapshots and denies post-approval script drift before execution.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.7`
- Patched version: `2026.3.8`

## Fix Commit(s)

- `c76d29208bf6a7f058d2cf582519d28069e42240`
- `cf3a479bd1204f62eef7dd82b4aa328749ae6c91`

## Release Verification

- npm `2026.3.7` remains vulnerable.
- npm `2026.3.8` contains the completed fix.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8g75-q649-6pv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32921
- https://github.com/openclaw/openclaw/commit/c76d29208bf6a7f058d2cf582519d28069e42240
- https://github.com/openclaw/openclaw/commit/cf3a479bd1204f62eef7dd82b4aa328749ae6c91
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-script-content-modification-via-mutable-operand-binding-in-system-run
