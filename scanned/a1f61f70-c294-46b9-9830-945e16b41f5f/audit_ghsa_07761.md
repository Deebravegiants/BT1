# [H] OpenClaw has an arbitrary transcript path file write via gateway sessionFile

## Summary
Severity: High
Advisory: GHSA-64qx-vpxx-mvqf
CVE: CVE-2026-28459
CWE: CWE-23, CWE-284, CWE-73, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-64qx-vpxx-mvqf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.12

## Details
## Summary

In OpenClaw versions prior to 2026.2.12, the gateway accepted an untrusted `sessionFile` path when resolving the session transcript file. This could allow an authenticated gateway client to create and append OpenClaw session transcript records at an arbitrary path on the gateway host.

## Affected Versions

- Affected: openclaw `< 2026.2.12`
- Patched: openclaw `>= 2026.2.12` (recommended: `>= 2026.2.13`)

## Impact

An authenticated gateway client could influence where the gateway writes transcript data by supplying `sessionFile` outside of the sessions directory. Depending on deployment and filesystem permissions, this may enable arbitrary file creation and repeated appends, leading to configuration corruption and/or denial of service.

This issue does not, by itself, provide a proven remote code execution path.

## Fix

The transcript path is now constrained to the sessions directory via `resolveSessionFilePath(...)` containment checks.

Fix commits:
- 4199f9889f0c307b77096a229b9e085b8d856c26
- (compat) 25950bcbb8ba4d8cde002557f6e27c219ae4deda

## Credits

Thanks to @tubadeligoz for the report.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-64qx-vpxx-mvqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-28459
- https://github.com/openclaw/openclaw/commit/25950bcbb8ba4d8cde002557f6e27c219ae4deda
- https://github.com/openclaw/openclaw/commit/4199f9889f0c307b77096a229b9e085b8d856c26
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-write-via-untrusted-sessionfile-path
