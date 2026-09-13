# [H] lodash vulnerable to Code Injection via `_.template` imports key names

## Summary
Severity: High
Advisory: GHSA-r5fr-rjxr-66jc
CVE: CVE-2026-4800
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-r5fr-rjxr-66jc
Type: github-advisory

## Affected
- npm: `lodash` — affected >=4.0.0 <4.18.0
- npm: `lodash-es` — affected >=4.0.0 <4.18.0
- npm: `lodash-amd` — affected >=4.0.0 <4.18.0
- npm: `lodash.template` — affected >=4.0.0 <4.18.0

## Details
### Impact

The fix for [CVE-2021-23337](https://github.com/advisories/GHSA-35jh-r3h4-6jhm) added validation for the `variable` option in `_.template` but did not apply the same validation to `options.imports` key names. Both paths flow into the same `Function()` constructor sink.

When an application passes untrusted input as `options.imports` key names, an attacker can inject default-parameter expressions that execute arbitrary code at template compilation time.

Additionally, `_.template` uses `assignInWith` to merge imports, which enumerates inherited properties via `for..in`. If `Object.prototype` has been polluted by any other vector, the polluted keys are copied into the imports object and passed to `Function()`.

### Patches

Users should upgrade to version 4.18.0.

The fix applies two changes:
1. Validate `importsKeys` against the existing `reForbiddenIdentifierChars` regex (same check already used for the `variable` option)
2. Replace `assignInWith` with `assignWith` when merging imports, so only own properties are enumerated

### Workarounds

Do not pass untrusted input as key names in `options.imports`. Only use developer-controlled, static key names.

## References
- https://github.com/lodash/lodash/security/advisories/GHSA-r5fr-rjxr-66jc
- https://nvd.nist.gov/vuln/detail/CVE-2026-4800
- https://github.com/lodash/lodash/commit/3469357cff396a26c363f8c1b5a91dde28ba4b1c
- https://cna.openjsf.org/security-advisories.html
- https://github.com/advisories/GHSA-35jh-r3h4-6jhm
- https://github.com/lodash/lodash
