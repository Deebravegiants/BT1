# [M] jackson-databind has a @JsonView bypass for unwrapped creator parameters

## Summary
Severity: Medium
Advisory: GHSA-rcqc-6cw3-h962
CVE: CVE-2026-54518
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-rcqc-6cw3-h962
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.21.0 <2.21.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
`UnwrappedPropertyHandler.processUnwrappedCreatorProperties()` replays buffered JSON into creator parameters but never consults `prop.visibleInView(activeView)`. The normal property-based creator path gates creator properties on the active view, but this unwrapped-creator replay path bypasses that check, so a constructor parameter annotated with both `@JsonView(AdminView.class)` and `@JsonUnwrapped` is populated from attacker JSON even when a more restrictive view is active.

## Impact
View-restricted unwrapped creator parameters can be set from untrusted input where `@JsonView` is used as a write-side authorization boundary.

## Affected / Patched (verified via `git tag --contains`)
- 2.21 line: `>= 2.21.0, < 2.21.4` -> fixed in **2.21.4** (backport `721fa07`, #5973)
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5971, `d633bc0`)

## Severity / CWE
Maintainer: minor. Reporter: HIGH. CWE-863 (Incorrect Authorization); related CWE-284.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-rcqc-6cw3-h962
- https://nvd.nist.gov/vuln/detail/CVE-2026-54518
- https://github.com/FasterXML/jackson-databind/pull/5971
- https://github.com/FasterXML/jackson-databind/pull/5973
- https://github.com/FasterXML/jackson-databind/commit/721fa07ebbd4aab4a659a1a68940878315c3e341
- https://github.com/FasterXML/jackson-databind/commit/d633bc038f200c1397c07f1a2b46f58e72c91eea
- https://github.com/FasterXML/jackson-databind
