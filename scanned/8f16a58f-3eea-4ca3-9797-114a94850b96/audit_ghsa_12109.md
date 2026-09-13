# [H] OpenClaw's hook transform module path allows traversal and arbitrary JavaScript module loading

## Summary
Severity: High
Advisory: GHSA-7xhj-55q9-pc3m
CVE: CVE-2026-28393
CWE: CWE-22, CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-7xhj-55q9-pc3m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2.0.0-beta3 <2026.2.14

## Details
## Summary

OpenClaw hook mapping transforms could be loaded via absolute paths or `..` traversal, allowing arbitrary JavaScript module loading/execution in the gateway process when an attacker can modify hooks configuration.

## Affected Versions

- Affected: >= 2.0.0-beta3 and <= 2026.2.13
- Fixed: 2026.2.14

## Details

`hooks.mappings[].transform.module` is dynamically imported and executed during webhook processing. Path resolution previously accepted absolute paths and did not enforce containment for relative paths, so a config-controlled transform could resolve outside the intended transforms directory.

## Impact

If an attacker can write the OpenClaw config (or otherwise update hooks config through authenticated configuration mechanisms), they could point a hook mapping transform at an arbitrary module on disk and execute code with the gateway process privileges.

## Reproduction (config-controlled module load)

1. Configure a hook mapping that points to a transform path that escapes the transforms directory (for example via `..` traversal).
2. Place a malicious ESM module at the resolved location that executes arbitrary code in the gateway process.
3. Trigger the hook endpoint with the correct hook token.

## Fix

Transform loading is now constrained to the OpenClaw transforms root directory:

- Root: `~/.openclaw/hooks/transforms`
- `hooks.transformsDir` must be within that directory
- `transform.module` must be within the selected transforms directory

Attempts to escape the root (absolute paths outside, `..` traversal) are rejected.

Fix commit(s):

- a0361b8ba959e8506dc79d638b6e6a00d12887e4
- 18e8bd68c5015a894f999c6d5e6e32468965bfb5

## Credits

OpenClaw thanks @akhmittra for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7xhj-55q9-pc3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-28393
- https://github.com/openclaw/openclaw/commit/18e8bd68c5015a894f999c6d5e6e32468965bfb5
- https://github.com/openclaw/openclaw/commit/a0361b8ba959e8506dc79d638b6e6a00d12887e4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-beta-arbitrary-javascript-module-loading-via-hook-transform-path-traversal
