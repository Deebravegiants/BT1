# [M] OpenClaw: diffs viewer misclassifies proxied remote requests as loopback when `allowRemoteViewer` is disabled

## Summary
Severity: Medium
Advisory: GHSA-3xv9-89fm-7h4r
CVE: CVE-2026-41403
CWE: CWE-348, CWE-807
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-3xv9-89fm-7h4r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
diffs viewer misclassifies proxied remote requests as loopback when `allowRemoteViewer` is disabled

## Current Maintainer Triage
- Status: open
- Normalized severity: low
- Assessment: Shipped v2026.3.28 misclassified proxied diff-viewer requests as local loopback in some cases, a real but low-severity access-control flaw.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `30a1690323088fd291abd11643a264a6828a002c` — 2026-03-30T14:17:27-06:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3xv9-89fm-7h4r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41403
- https://github.com/openclaw/openclaw/commit/30a1690323088fd291abd11643a264a6828a002c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-access-control-bypass-via-proxied-remote-request-misclassification
