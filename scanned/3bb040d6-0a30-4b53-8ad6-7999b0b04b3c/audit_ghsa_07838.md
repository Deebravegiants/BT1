# [C] OpenClaw is vulnerable to validation bypass through GNU long-option abbreviations in allowlist mode

## Summary
Severity: Critical
Advisory: GHSA-7977-c43c-xpwj
CVE: CVE-2026-28363
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-27
Source: https://github.com/advisories/GHSA-7977-c43c-xpwj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
In OpenClaw before 2026.2.23, tools.exec.safeBins validation for sort could be bypassed via GNU long-option abbreviations (such as --compress-prog) in allowlist mode, leading to approval-free execution paths that were intended to require approval. Only an exact string such as --compress-program was denied.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3c6h-g97w-fg78
- https://nvd.nist.gov/vuln/detail/CVE-2026-28363
- https://github.com/openclaw/openclaw/commit/3b8e33037ae2e12af7beb56fcf0346f1f8cbde6f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.23
