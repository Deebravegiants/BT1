# [M] OpenClaw: Trailing-dot localhost CDP hosts could bypass remote loopback protections

## Summary
Severity: Medium
Advisory: GHSA-fh32-73r9-rgh5
CVE: CVE-2026-41372
CWE: CWE-20, CWE-639
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-fh32-73r9-rgh5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, remote CDP discovery could return a trailing-dot localhost host such as `localhost.` and bypass OpenClaw's loopback-host normalization. That let a non-loopback remote CDP profile pivot the follow-up connection back onto localhost.

## Impact

A hostile discovery response could retarget authenticated browser control toward a localhost-resolving endpoint on the OpenClaw host. This weakened the existing remote-CDP loopback protection and could expose localhost-backed browser state.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `9c22d636697336a6b22b0ae24798d8b8325d7828` — normalize localhost absolute-form CDP hosts before loopback checks

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fh32-73r9-rgh5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41372
- https://github.com/openclaw/openclaw/commit/9c22d636697336a6b22b0ae24798d8b8325d7828
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-loopback-protection-bypass-via-trailing-dot-localhost-in-cdp-discovery
