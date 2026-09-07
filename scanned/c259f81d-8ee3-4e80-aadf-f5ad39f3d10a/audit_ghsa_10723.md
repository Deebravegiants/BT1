# [M] OpenClaw: Empty approver lists could grant explicit approval authorization

## Summary
Severity: Medium
Advisory: GHSA-49cg-279w-m73x
CVE: CVE-2026-43574
CWE: CWE-183, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-49cg-279w-m73x
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.12

## Details
## Summary

Empty approver lists could grant explicit approval authorization.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.12`
- Patched versions: `>= 2026.4.12`

## Impact

For helper-backed channels, an empty resolved approver list could be interpreted as explicit approval authorization, allowing a sender outside the normal channel authorization gate to resolve pending approvals if they knew an approval id.

## Technical Details

The fix prevents empty approver lists from granting explicit approval authorization and adds regression coverage for unauthorized senders.

## Fix

The issue was fixed in #65714. The first stable tag containing the fix is `v2026.4.12`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `0a105c0900de701d2ee9f1abc96b017afbd0afdd`
- PR: #65714

## Release Process Note

Users should upgrade to `openclaw` 2026.4.12 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @anshumanbh for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-49cg-279w-m73x
- https://nvd.nist.gov/vuln/detail/CVE-2026-43574
- https://github.com/openclaw/openclaw/pull/65714
- https://github.com/openclaw/openclaw/commit/0a105c0900de701d2ee9f1abc96b017afbd0afdd
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-improper-authorization-via-empty-approver-lists
