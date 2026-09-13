# [H] OpenClaw Node host system.run rawCommand/command mismatch can bypass allowlist/approvals

## Summary
Severity: High
Advisory: GHSA-h3f9-mjwj-w476
CVE: CVE-2026-26325
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-h3f9-mjwj-w476
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary

A mismatch between `rawCommand` and `command[]` in the node host `system.run` handler could cause allowlist/approval evaluation to be performed on one command while executing a different argv.

## Affected Configurations

This only impacts deployments that:

- Use the node host / companion node execution path (`system.run` on a node).
- Enable allowlist-based exec policy (`security=allowlist`) with approval prompting driven by allowlist misses (for example `ask=on-miss`).
- Allow an attacker to invoke `system.run`.

Default/non-node configurations are not affected.

## Impact

In affected configurations, an attacker who can invoke `system.run` can bypass allowlist enforcement and approval prompts by supplying an allowlisted `rawCommand` while providing a different `command[]` argv for execution.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.13`
- Patched version: `>= 2026.2.14` (planned next release)

## Fix

Enforce `rawCommand`/`command[]` consistency (gateway fail-fast + node host validation).

## Fix Commit(s)

- cb3290fca32593956638f161d9776266b90ab891

## Release Process Note

This advisory pre-sets the patched version to the planned next release (`2026.2.14`). Once `openclaw@2026.2.14` is published to npm, the advisory can be published without further edits.

Thanks @christos-eth for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h3f9-mjwj-w476
- https://nvd.nist.gov/vuln/detail/CVE-2026-26325
- https://github.com/openclaw/openclaw/commit/cb3290fca32593956638f161d9776266b90ab891
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
