# [M] OpenClaw skills-install-download: tar.bz2 extraction bypassed archive safety parity checks (local DoS)

## Summary
Severity: Medium
Advisory: GHSA-77hf-7fqf-f227
CWE: CWE-400, CWE-409
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-77hf-7fqf-f227
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
The `tar.bz2` installer path in `src/agents/skills-install-download.ts` used shell tar preflight/extract logic that did not share the same hardening guarantees as the centralized archive extractor.

This allowed crafted `.tar.bz2` archives to bypass special-entry blocking and extracted-size guardrails enforced on other archive paths, causing local availability impact during skill install.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published at triage time: `2026.3.1`
- Affected range: `<= 2026.3.1`
- Patched in: `2026.3.2` (released)

### Impact
Local DoS / availability impact when processing untrusted `.tar.bz2` skill archives.

### Fix Commit(s)
- `0dbb92dd2bcf9a32379d11c0f11ed016669dae3e`

### Related advisories
- Canonical overlap (closed): GHSA-3pj7-x8jr-jvj8
- Duplicate variant (closed): GHSA-rgr7-g85h-6v82

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-77hf-7fqf-f227
- https://github.com/openclaw/openclaw/commit/0dbb92dd2bcf9a32379d11c0f11ed016669dae3e
- https://github.com/openclaw/openclaw
