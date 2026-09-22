# [M] OpenClaw has stored XSS in exported session HTML viewer via markdown/raw-HTML rendering

## Summary
Severity: Medium
Advisory: GHSA-r294-2894-92j3
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-r294-2894-92j3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
## Summary

The exported session HTML viewer allowed stored XSS when untrusted session content included raw HTML markdown tokens or unescaped metadata fields.

## Impact

Opening a crafted exported HTML session could execute attacker-controlled JavaScript in the viewer context. This can expose session content in the page and enable phishing or UI spoofing in the trusted export view.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.22-2`
- Patched version (released): `>= 2026.2.23`

## Technical Details

The exporter rendered markdown with `marked.parse(...)` and inserted HTML via `innerHTML`, but did not override the `html` renderer token path. Raw HTML (for example `<img ... onerror=...>`) was passed through. Additional tree/header metadata fields were interpolated without escaping in the export template.

## Reproduction

1. Create a session containing content like `<img src=x onerror=alert(1)>`.
2. Export the session to HTML.
3. Open the exported file.
4. Observe script execution from injected content.

## Remediation

- Added a `marked` `html(token)` renderer override that escapes raw HTML tokens.
- Escaped previously unescaped tree/header metadata fields in the export template.
- Added image MIME sanitization for exported data-URL image rendering.
- Added regression tests for markdown/token and metadata escaping paths.

## Fix Commit(s)

- `f8524ec77a3999d573e6c6b8a5055bf35c49a2e6`

## Release Process Note

`patched_versions` is pre-set to the released version (`>= 2026.2.23`). This advisory now reflects released fix version `2026.2.23`.

OpenClaw thanks @allsmog for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r294-2894-92j3
- https://github.com/openclaw/openclaw/commit/f8524ec77a3999d573e6c6b8a5055bf35c49a2e6
- https://github.com/openclaw/openclaw
