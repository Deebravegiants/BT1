# [M] OpenClaw vulnerable to path traversal (Zip Slip) in archive extraction during explicit installation commands

## Summary
Severity: Medium
Advisory: GHSA-v892-hwpg-jwqp
CVE: CVE-2026-28486
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-v892-hwpg-jwqp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.16-2 <2026.2.14

## Details
## Summary

A path traversal (Zip Slip) issue in archive extraction during explicit installation commands could allow a crafted archive to write files outside the intended extraction directory.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `>=2026.1.16-2 <2026.2.14`
- Fixed version: `2026.2.14`

## Affected Commands / Flows

This only affects users who run installation commands against an untrusted archive (local file or download URL), for example:

- `openclaw skills install` (download+extract installers)
- `openclaw hooks install` (archive installs)
- `openclaw plugins install` (archive installs)
- `openclaw signal install` (signal-cli asset extraction)

It is not triggered by receiving messages or normal gateway operation.

## Impact

Arbitrary file write as the current user. In the worst case this can be used for persistence or code execution if an attacker can convince a user to install a crafted archive.

## Fix

- Fix commit: `3aa94afcfd12104c683c9cad81faf434d0dadf87`
- Released in: `2026.2.14`

## Credits

OpenClaw thanks @markmusson for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v892-hwpg-jwqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-28486
- https://github.com/openclaw/openclaw/commit/3aa94afcfd12104c683c9cad81faf434d0dadf87
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-zip-slip-in-archive-extraction-via-installation-commands
