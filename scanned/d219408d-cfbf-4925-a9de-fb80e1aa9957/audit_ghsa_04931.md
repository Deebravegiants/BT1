# [M] MCPVault: PathFilter restricted directories (.git/.obsidian/node_modules) only denied at vault root, not nested

## Summary
Severity: Medium
Advisory: GHSA-9c83-rr99-vfwj
CVE: CVE-2026-57442
CWE: CWE-22, CWE-538
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9c83-rr99-vfwj
Type: github-advisory

## Affected
- npm: `@bitbonsai/mcpvault` — affected >=0 <0.11.5

## Details
PathFilter's deny-list glob patterns are anchored, so `.git`, `.obsidian`, and `node_modules` were only blocked at the vault root. Nested copies inside the vault (e.g. `tools/cli/node_modules/...`, `tools/somerepo/.git/config`, a nested `.obsidian/`) were fully traversable via isAllowed/isAllowedForListing. Impact: a nested `.git/config` (remote URLs / embedded tokens) and nested `.obsidian` contents could be read, under the same prompt-injection threat model as GHSA-j99q-93c9-h869 (an attacker influences the path an agent reads). It also caused nested `node_modules` to pollute the tag index (#128, the public symptom). Fixed in 0.11.5 by denying these restricted names at any path depth (matched case-insensitively as any path segment).

## References
- https://github.com/bitbonsai/mcpvault/security/advisories/GHSA-9c83-rr99-vfwj
- https://github.com/bitbonsai/mcpvault
