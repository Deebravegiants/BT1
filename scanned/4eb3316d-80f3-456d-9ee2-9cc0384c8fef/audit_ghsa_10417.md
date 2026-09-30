# [M] OpenClaw: Heartbeat owner downgrade missed untrusted webhook wake events

## Summary
Severity: Medium
Advisory: GHSA-g2hm-779g-vm32
CVE: CVE-2026-43566
CWE: CWE-184, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-g2hm-779g-vm32
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.7 <2026.4.14

## Details
## Summary

Heartbeat owner downgrade missed untrusted webhook wake events.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `>= 2026.4.7 < 2026.4.14`
- Patched versions: `>= 2026.4.14`

## Impact

Heartbeat owner downgrade logic could skip webhook wake events carrying untrusted content, preserving owner-like execution context where the run should have been downgraded.

## Technical Details

The fix includes wake and hook event reasons in owner-downgrade inspection and forces downgrade for untrusted hook wake events.

## Fix

The issue was fixed in #66031. The first stable tag containing the fix is `v2026.4.14`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `31281bc92f55796817a92bc43f722cba1e77ab42`
- PR: #66031

## Release Process Note

Users should upgrade to `openclaw` 2026.4.14 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @zsxsoft, with sponsorship from @KeenSecurityLab and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g2hm-779g-vm32
- https://nvd.nist.gov/vuln/detail/CVE-2026-43566
- https://github.com/openclaw/openclaw/pull/66031
- https://github.com/openclaw/openclaw/commit/31281bc92f55796817a92bc43f722cba1e77ab42
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-untrusted-webhook-wake-events
