# [H] OpenClaw has an exec allowlist bypass via command substitution/backticks inside double quotes

## Summary
Severity: High
Advisory: GHSA-3hcm-ggvf-rch5
CVE: CVE-2026-28470
CWE: CWE-78, CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-3hcm-ggvf-rch5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.2

## Details
### Summary

Exec approvals allowlist bypass via command substitution/backticks inside double quotes.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.1`
- Fixed: `>= 2026.2.2`

### Impact

Only affects setups that explicitly enable the optional exec approvals allowlist feature. Default installs are unaffected.

### Fix

Reject unescaped `$()` and backticks inside double quotes during allowlist analysis.

### Fix Commit(s)

- d1ecb46076145deb188abcba8f0699709ea17198

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3hcm-ggvf-rch5
- https://nvd.nist.gov/vuln/detail/CVE-2026-28470
- https://github.com/openclaw/openclaw/commit/d1ecb46076145deb188abcba8f0699709ea17198
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.2
- https://www.vulncheck.com/advisories/openclaw-exec-allowlist-bypass-via-command-substitution-in-double-quotes
