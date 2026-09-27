# [H] OpenClaw's TOCTOU symlink race in writeFileWithinRoot could create or truncate files outside root boundaries

## Summary
Severity: High
Advisory: GHSA-x82f-27x3-q89c
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-x82f-27x3-q89c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
A symlink-retarget TOCTOU race in `writeFileWithinRoot` could point an attacker-controlled path alias outside the configured root between resolution and write operations.

### Impact
Affected versions could cause out-of-root write side effects (including file creation or truncation) before final boundary validation.

### Fix
Root-scoped write flow now opens existing files without pre-truncation, creates missing files with exclusive create semantics, truncates only after post-open identity/boundary checks, and removes out-of-root artifacts when a race is detected.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x82f-27x3-q89c
- https://github.com/openclaw/openclaw
