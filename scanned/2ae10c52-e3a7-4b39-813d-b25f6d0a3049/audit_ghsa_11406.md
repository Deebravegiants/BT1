# [H] OpenClaw: Node-host approvals could show misleading shell payloads instead of the executed argv

## Summary
Severity: High
Advisory: GHSA-rw39-5899-8mxp
CVE: CVE-2026-32971
CWE: CWE-436, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-rw39-5899-8mxp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, node-host `system.run` approvals could display only an extracted shell payload such as `jq --version` while execution still ran a different outer wrapper argv such as `./env sh -c 'jq --version'`.

## Impact
This is an approval-integrity bug. An attacker who could place or select a local wrapper binary and induce a wrapper-shaped command could get local code executed after the operator approved misleading command text.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.8`
- Fixed in: `2026.3.11`

## Technical Details
Wrapper resolution normalized executables by basename and extracted inner shell payload text for approval display, while execution still preserved the full wrapper argv. Approval storage and UI therefore showed text that did not match the exact command OpenClaw would execute.

## Fix
OpenClaw now binds approvals to the exact executed argv and keeps extracted shell payload text only as secondary preview data. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rw39-5899-8mxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-32971
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-node-host-approval-ui-mismatch-allows-execution-of-unintended-commands
