# [M] OpenClaw: Feishu extension resolveUploadInput bypasses file-system sandbox and allows arbitrary file reads via upload_image

## Summary
Severity: Medium
Advisory: GHSA-qf48-qfv4-jjm9
CVE: CVE-2026-41363
CWE: CWE-22, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-qf48-qfv4-jjm9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.2.6 <2026.3.28

## Details
## Summary

Feishu upload path resolution could read files outside the configured localRoots sandbox before handing them to the upload path.

## Impact

A tool caller constrained to workspace or localRoots paths could exfiltrate arbitrary host files through Feishu upload actions.

## Affected Component

`extensions/feishu/src/docx.ts`

## Fixed Versions

- Affected: `>= 2026.2.6, <= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `764394c78b` (`fix: enforce localRoots sandbox on Feishu docx upload file reads`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qf48-qfv4-jjm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41363
- https://github.com/openclaw/openclaw/commit/764394c78b6c22c5b53c3cd132d27ff36340bf45
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-feishu-upload-image-parameter
