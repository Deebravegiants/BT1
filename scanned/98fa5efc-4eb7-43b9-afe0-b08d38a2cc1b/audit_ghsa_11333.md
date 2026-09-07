# [H] OpenClaw: Sandbox staged writes could escape the verified parent directory before commit

## Summary
Severity: High
Advisory: GHSA-mj4p-rc52-m843
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-mj4p-rc52-m843
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
## Summary
In affected versions of `openclaw`, sandbox fs-bridge writes validated the destination before commit, but temporary file creation and population were not pinned to a verified parent directory. A raced parent-path alias change could cause the staged temp file to be created outside the intended writable mount before the final guarded replace step.

## Impact
This is a sandbox boundary bypass affecting integrity and availability within the writable mount scope. Attacker-controlled bytes could be written outside the intended validated path before the final guarded step ran.

## Affected Packages and Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.8`
- Fixed in: `2026.3.11`

## Technical Details
The older staging flow created and wrote the temporary file using target-directory shell path operations before the final replace step revalidated the destination. That meant the last guard protected only the final rename, not the earlier temp-file materialization path.

## Fix
OpenClaw now resolves a pinned mount root plus relative parent path, creates the temporary file inside the verified parent directory, and performs the final atomic replace from that pinned directory context. The fix shipped in `openclaw@2026.3.11`.

## Workarounds
Upgrade to `2026.3.11` or later.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mj4p-rc52-m843
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
