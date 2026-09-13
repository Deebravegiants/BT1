# [H] @tmlmobilidade/utils has prototype pollution in its setValueAtPath

## Summary
Severity: High
Advisory: GHSA-cmxg-94mg-jq94
CVE: CVE-2026-45325
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-cmxg-94mg-jq94
Type: github-advisory

## Affected
- npm: `@tmlmobilidade/utils` — affected >=0 <20260509.0340.15

## Details
### Impact
Prototype pollution vulnerability in @tmlmobilidade/utils for setValueAtPath().

### Patches
A fix is available in versions 20260509.0340.15 and up.

## References
- https://github.com/tmlmobilidade/go/security/advisories/GHSA-cmxg-94mg-jq94
- https://github.com/tmlmobilidade/go/commit/b10505baa7ba0701f830a05f3007c0a6bdd00eb7
- https://github.com/tmlmobilidade/go
- https://github.com/tmlmobilidade/go/blob/prd/packages/utils/src/generic/value-at-path.ts
