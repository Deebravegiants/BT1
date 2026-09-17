# [H] OpenClaw has Zip Slip path traversal in tar archive extraction

## Summary
Severity: High
Advisory: GHSA-p25h-9q54-ffvw
CVE: CVE-2026-28453
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-p25h-9q54-ffvw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary
OpenClaw versions before 2026.2.14 did not sufficiently validate TAR archive entry paths during extraction. A crafted archive could use path traversal sequences (for example `../../...`) to write files outside the intended destination directory (Zip Slip).

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `< 2026.2.14`
- Fixed: `>= 2026.2.14`

## Details
The affected code path is `extractArchive()` in `src/infra/archive.ts`. Prior to 2026.2.14, TAR extraction used `tar.x({ cwd: destDir })` without rejecting traversal and absolute entry paths.

This extraction is used by installation flows such as:
- `openclaw plugins install …`
- `openclaw hooks install …`

## Impact
If a user installs an untrusted `.tar` / `.tgz` archive, an attacker can write files outside the extraction directory (within the permissions of the OpenClaw process). This can lead to configuration tampering and potentially code execution.

## Mitigation
Upgrade to `openclaw >= 2026.2.14`. Avoid installing untrusted plugin/hook archives.

## Fix Commit(s)
- `3aa94afcfd12104c683c9cad81faf434d0dadf87`

OpenClaw thanks @xuemian168 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p25h-9q54-ffvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-28453
- https://github.com/openclaw/openclaw/commit/3aa94afcfd12104c683c9cad81faf434d0dadf87
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-zip-slip-path-traversal-in-tar-archive-extraction
