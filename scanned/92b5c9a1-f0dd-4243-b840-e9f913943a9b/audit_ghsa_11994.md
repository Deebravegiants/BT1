# [H] OpenClaw has command injection via Windows shell fallback in Lobster tool execution

## Summary
Severity: High
Advisory: GHSA-7fcc-cw49-xm78
CVE: CVE-2026-32000
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-7fcc-cw49-xm78
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Summary

The Lobster extension tool execution path used a Windows shell fallback (`shell: true`) after spawn failures (`EINVAL`/`ENOENT`). In that fallback path, shell metacharacters in command arguments can be interpreted by the shell, enabling command injection.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.17`
- Latest confirmed affected published version: `2026.2.17`
- Patched version: `2026.2.19`

## Technical Details

In affected releases (including `v2026.2.17`), `extensions/lobster/src/lobster-tool.ts` retried subprocess launch with `shell: true` on Windows for `EINVAL`/`ENOENT` spawn errors. The fix removes shell fallback and resolves Windows wrappers to explicit executable/script argv execution.

## Fix Commit(s)

- `ba7be018da354ea9f803ed356d20464df0437916`

OpenClaw thanks @allsmog for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7fcc-cw49-xm78
- https://github.com/openclaw/openclaw/commit/ba7be018da354ea9f803ed356d20464df0437916
- https://github.com/openclaw/openclaw
