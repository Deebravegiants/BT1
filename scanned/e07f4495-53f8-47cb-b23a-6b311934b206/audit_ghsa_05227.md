# [M] MCPVault: PathFilter restricted-directory deny-list bypass via case and trailing dot/space equivalence

## Summary
Severity: Medium
Advisory: GHSA-j99q-93c9-h869
CVE: CVE-2026-57441
CWE: CWE-178, CWE-41
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-j99q-93c9-h869
Type: github-advisory

## Affected
- npm: `@bitbonsai/mcpvault` — affected >=0 <0.11.4

## Details
On case-insensitive filesystems (macOS, Windows), PathFilter compiled its deny-list patterns case-sensitively and matched the path verbatim, so names like `.Git/config`, `.GIT/config`, or `.oBsIdIaN/secrets.md` slipped past the `.git`/`.obsidian`/`node_modules` restriction while the OS opened the real file. On Windows, trailing dots/spaces (`.git./config`, `.git /config`) bypassed it the same way. Affects both `isAllowed` (read/write/move/search) and `isAllowedForListing`. Vault-root `..` containment is NOT affected. Fixed in 0.11.4 by case-insensitive matching plus per-segment canonicalization before the deny-list check. Reported privately by novice-22.

## References
- https://github.com/bitbonsai/mcpvault/security/advisories/GHSA-j99q-93c9-h869
- https://github.com/bitbonsai/mcpvault
