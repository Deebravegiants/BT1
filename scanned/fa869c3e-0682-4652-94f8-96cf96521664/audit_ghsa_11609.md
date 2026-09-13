# [H] OpenClaw: Workspace plugin auto-discovery allowed code execution from cloned repositories

## Summary
Severity: High
Advisory: GHSA-99qw-6mr3-36qr
CVE: CVE-2026-32920
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-99qw-6mr3-36qr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

OpenClaw automatically discovered and loaded plugins from `.openclaw/extensions/` inside the current workspace without an explicit trust or install step. A malicious repository could include a crafted workspace plugin that executed as soon as a user ran OpenClaw from that cloned directory.

### Impact

Opening or running OpenClaw in an untrusted repository could lead to arbitrary code execution under the user's account.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Workspace plugin loading now requires explicit trusted state before execution. Users should update to `2026.3.12` or later and avoid running OpenClaw inside untrusted repositories on older releases.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-99qw-6mr3-36qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32920
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
- https://www.vulncheck.com/advisories/openclaw-arbitrary-code-execution-via-auto-discovery-of-workspace-plugins
