# [M] Electron: contextBridge object copy honors prototype setters

## Summary
Severity: Medium
Advisory: GHSA-ff2p-hmqr-hxm4
CVE: CVE-2026-70610
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-ff2p-hmqr-hxm4
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <39.8.9
- npm: `electron` — affected >=40.0.0-alpha.1 <40.9.2
- npm: `electron` — affected >=41.0.0-alpha.1 <41.2.2
- npm: `electron` — affected >=42.0.0-alpha.1 <42.0.0-beta.4

## Details
### Impact
Objects copied across the `contextBridge` boundary from untrusted content could carry an attacker-influenced prototype, enabling prototype-pollution-style attacks against preload code despite context isolation being enabled.

Apps are only affected if their preload code accepts object arguments from untrusted content and reads properties from them without own-property checks. Apps that only accept primitive arguments, or that validate object arguments, are not affected.

### Workarounds
Validate objects received from untrusted content with own-property checks (`Object.hasOwn`), or copy them onto a null-prototype object before use.

### Fixed Versions
* `42.0.0-beta.4`
* `41.2.2`
* `40.9.2`
* `39.8.9`

### For more information
If you have any questions or comments about this advisory, email Electron at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-ff2p-hmqr-hxm4
- https://github.com/electron/electron/pull/51083
- https://github.com/electron/electron/pull/51084
- https://github.com/electron/electron/pull/51085
- https://github.com/electron/electron/pull/51086
- https://github.com/electron/electron/commit/17d5d26499cd279fab48f5f26527f8edc02a7713
- https://github.com/electron/electron/commit/23a6efb714dec80e2cf45d3054d18d701162e4dd
- https://github.com/electron/electron/commit/4ac50292d552fb510eb778392620c85308770a55
- https://github.com/electron/electron/commit/5b699544cbbed51bedb7c60d75c8c42be5825737
- https://github.com/electron/electron
- https://github.com/electron/electron/releases/tag/v39.8.9
- https://github.com/electron/electron/releases/tag/v40.9.2
- https://github.com/electron/electron/releases/tag/v41.2.2
- https://github.com/electron/electron/releases/tag/v42.0.0-beta.4
