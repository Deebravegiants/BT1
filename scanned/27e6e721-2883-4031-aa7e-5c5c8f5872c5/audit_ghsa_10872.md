# [M] OpenClaw vulnerable to path traversal in Feishu media temp-file naming allows writes outside os.tmpdir()

## Summary
Severity: Medium
Advisory: GHSA-vj3g-5px3-gr46
CVE: CVE-2026-22171
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-vj3g-5px3-gr46
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Summary

OpenClaw’s Feishu media download flow used untrusted Feishu media keys (`imageKey` / `fileKey`) when building temporary file paths in `extensions/feishu/src/media.ts`.
Because those keys were interpolated directly into temp-file paths, traversal segments could escape the temp directory and redirect writes outside `os.tmpdir()`.

## Impact

This is an arbitrary file write issue (within the OpenClaw process file permissions).
If an attacker can control Feishu media key values returned to the client (for example via compromised upstream response path), they can influence where downloaded bytes are written.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published npm version at triage: `2026.2.17`
- Affected versions: `<= 2026.2.17`
- Fixed version: `2026.2.19`

## Fix Commit(s)

- `c821099157a9767d4df208c6b12f214946507871`
- `cdb00fe2428000e7a08f9b7848784a0049176705`
- `ec232a9e2dff60f0e3d7e827a7c868db5254473f`

## Remediation

The fix removes key-derived temp-file naming and keeps downloads in safe temp locations. Additional hardening isolates SDK `writeFile` calls in per-download temp directories (`mkdtemp`) with deterministic cleanup, enforces Feishu key trust-boundary validation, and adds a repository guard test against dynamic `path.join(os.tmpdir(), \`...${...}\`)` patterns in runtime code.

OpenClaw thanks @allsmog for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vj3g-5px3-gr46
- https://nvd.nist.gov/vuln/detail/CVE-2026-22171
- https://github.com/openclaw/openclaw/commit/c821099157a9767d4df208c6b12f214946507871
- https://github.com/openclaw/openclaw/commit/cdb00fe2428000e7a08f9b7848784a0049176705
- https://github.com/openclaw/openclaw/commit/ec232a9e2dff60f0e3d7e827a7c868db5254473f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-in-feishu-media-temporary-file-naming
