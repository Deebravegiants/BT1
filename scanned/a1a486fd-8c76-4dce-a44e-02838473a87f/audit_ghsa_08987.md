# [M] OpenClaw's exec allowlist analysis rejects shell expansion in unquoted heredocs

## Summary
Severity: Medium
Advisory: GHSA-x3h8-jrgh-p8jx
CWE: CWE-200
Ecosystem: npm
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-x3h8-jrgh-p8jx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
Exec allowlist analysis rejects shell expansion in unquoted heredocs


## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
An allowlisted command containing an unquoted heredoc could hide shell expansion in the heredoc body. That could make the approved command text look safer than what the shell would evaluate at runtime.

## Fix
The exec command analyzer now tracks heredoc bodies, rejects unquoted heredoc expansion tokens and continuation-splice bypasses, and preserves quoted heredocs and literal safe text.

## Fix Commit(s)
- b2e8b7d4bb2f22eaa16f5c4b07547774e90b65a5

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

Thanks @VladimirEliTokarev for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x3h8-jrgh-p8jx
- https://github.com/openclaw/openclaw/commit/b2e8b7d4bb2f22eaa16f5c4b07547774e90b65a5
- https://github.com/openclaw/openclaw
