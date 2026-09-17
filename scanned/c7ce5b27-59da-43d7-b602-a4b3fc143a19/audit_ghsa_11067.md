# [H] OpenClaw is vulnerable to Path Traversal through path validation bypass

## Summary
Severity: High
Advisory: GHSA-hggm-x7r9-mm7v
CVE: CVE-2026-32846
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-hggm-x7r9-mm7v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.03.28

## Details
OpenClaw through 2026.3.23 (fixed in commit 4797bbc) contains a path traversal vulnerability in media parsing that allows attackers to read arbitrary files by bypassing path validation in the isLikelyLocalPath() and isValidMedia() functions. Attackers can exploit incomplete validation and the allowBareFilename bypass to reference files outside the intended application sandbox, resulting in disclosure of sensitive information including system files, environment files, and SSH keys.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f6pf-4gjx-c94r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32846
- https://github.com/openclaw/openclaw/pull/54642
- https://github.com/openclaw/openclaw/commit/4797bbc5b96e2cca5532e43b58915c051746fe37
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-media-parsing-path-traversal-to-arbitrary-file-read
