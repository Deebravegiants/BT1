# [M] jackson-databind has @JsonView bypass for setterless creator properties

## Summary
Severity: Medium
Advisory: GHSA-5hh8-q8hv-fr38
CVE: CVE-2026-54517
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-5hh8-q8hv-fr38
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.21.0 <2.21.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
In `BeanDeserializer._deserializeUsingPropertyBased`, the active-view (`@JsonView`) filter was applied only to creator properties; the regular property-buffering branch performed no `prop.visibleInView(activeView)` check. A change making `SetterlessProperty.isMerging()` return `true` routed setterless Collection/Map properties through this unguarded path, so a setterless collection annotated with a restricted `@JsonView` is populated from attacker JSON even when the active view excludes it.

## Impact
View-restricted (e.g. admin-only) setterless collection/map properties can be written from untrusted JSON despite `@JsonView` gating — an access-control / mass-assignment bypass. No RCE or DoS.

## Affected / Patched (verified via `git tag --contains`)
- 2.21 line: `>= 2.21.0, < 2.21.4` -> fixed in **2.21.4** (backport `94c5d21`, #5970)
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5969, `5bf23ed`)

## Severity / CWE
Maintainer: minor. Reporter: HIGH. CWE-863 (Incorrect Authorization); related CWE-1220.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-5hh8-q8hv-fr38
- https://nvd.nist.gov/vuln/detail/CVE-2026-54517
- https://github.com/FasterXML/jackson-databind/pull/5969
- https://github.com/FasterXML/jackson-databind/pull/5970
- https://github.com/FasterXML/jackson-databind/commit/5bf23edb4221f7dd2ec8e71ff6d26c61640f261d
- https://github.com/FasterXML/jackson-databind/commit/94c5d215b3af1505098c686405d9641f041a9962
- https://github.com/FasterXML/jackson-databind
