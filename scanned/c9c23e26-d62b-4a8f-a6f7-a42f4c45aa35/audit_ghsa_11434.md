# [M] OpenClaw: Sandbox `writeFile` commit could race outside the validated path

## Summary
Severity: Medium
Advisory: GHSA-xvx8-77m6-gwg6
CVE: CVE-2026-32977
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-xvx8-77m6-gwg6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, the sandbox fs-bridge `writeFile` commit step used an unanchored container path during the final move into place. An attacker racing parent-path changes inside the sandbox could redirect the committed file outside the validated sandbox path.

## Impact
This is a sandbox boundary bypass. In-sandbox code could win a time-of-check-time-of-use race and cause host-approved `writeFile` operations to land outside the validated writable path within the container mount namespace.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `< 2026.3.11`
- Fixed in: `2026.3.11`

## Technical Details
The hardening work for anchored remove, rename, and mkdir operations did not fully cover the `writeFile` commit path. The final `mv` still used the raw target path, leaving a race window between safety revalidation and the in-container commit step.

## Fix
OpenClaw now anchors the `writeFile` commit path to the canonical parent directory before the final move. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xvx8-77m6-gwg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-32977
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
- https://www.vulncheck.com/advisories/openclaw-sandbox-boundary-bypass-via-unanchored-writefile-commit-path
