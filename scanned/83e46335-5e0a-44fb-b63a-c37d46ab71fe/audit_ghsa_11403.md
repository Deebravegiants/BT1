# [H] OpenClaw: stageSandboxMedia destination symlink traversal can overwrite files outside sandbox workspace

## Summary
Severity: High
Advisory: GHSA-cfvj-7rx7-fc7c
CVE: CVE-2026-31990
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-cfvj-7rx7-fc7c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
`stageSandboxMedia` allowed destination symlink traversal during media staging, which could overwrite files outside the sandbox workspace root.

### Impact
When sandbox media staging handled inbound files, destination writes under `media/inbound` were not destination-alias-safe. If a symlink existed in that destination path, the write could follow it and overwrite host files outside the intended sandbox workspace boundary.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version checked: `2026.3.1`
- Affected: `<= 2026.3.1`
- Patched versions: `>= 2026.3.2` (released)

### Root Cause
`stageSandboxMedia` validated source paths but wrote destination files with a direct copy path that did not enforce destination boundary/alias checks.

### Remediation
The fix routes staging writes through root-scoped safe write primitives for both local and SCP-staged attachments, preventing destination symlink traversal escapes.

### Fix Commit(s)
- `17ede52a4be3034f6ec4b883ac6b81ad0101558a`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cfvj-7rx7-fc7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-31990
- https://github.com/openclaw/openclaw/commit/17ede52a4be3034f6ec4b883ac6b81ad0101558a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-traversal-in-stagesandboxmedia-destination
