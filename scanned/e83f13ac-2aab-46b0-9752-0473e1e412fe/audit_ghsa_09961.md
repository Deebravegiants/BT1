# [M] OpenClaw: Browser tabs action select and close routes bypassed SSRF policy

## Summary
Severity: Medium
Advisory: GHSA-rj2p-j66c-mgqh
CVE: CVE-2026-42439
CWE: CWE-862, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-rj2p-j66c-mgqh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.10

## Details
## Summary

Browser tabs action select and close routes bypassed SSRF policy.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.10`
- Patched versions: `>= 2026.4.10`

## Impact

The browser `/tabs/action` select and close branches could operate on targets without enforcing configured browser SSRF policy, weakening tab-level navigation protections.

## Technical Details

The fix enforces browser SSRF policy in the select and close tab-action branches.

## Fix

The issue was fixed in #63332. The first stable tag containing the fix is `v2026.4.10`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `48c0347921b7e9438af0312968fc360ca88023f3`
- PR: #63332

## Release Process Note

Users should upgrade to `openclaw` 2026.4.10 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @tdjackey for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rj2p-j66c-mgqh
- https://nvd.nist.gov/vuln/detail/CVE-2026-42439
- https://github.com/openclaw/openclaw/pull/63332
- https://github.com/openclaw/openclaw/commit/48c03479211799ec3c1305ad69037cea25ba0e1e
- https://github.com/openclaw/openclaw/commit/48c0347921b7e9438af0312968fc360ca88023f3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-ssrf-policy-bypass-in-browser-tabs-action-routes
