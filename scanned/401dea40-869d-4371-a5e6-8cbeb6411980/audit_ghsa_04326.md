# [M] jackson-databind has case-insensitive deserialization bypasses per-property @JsonIgnoreProperties

## Summary
Severity: Medium
Advisory: GHSA-5jmj-h7xm-6q6v
CVE: CVE-2026-54515
CWE: CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-5jmj-h7xm-6q6v
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.1.0 <3.1.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.1.0 <3.1.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.18.9
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.5
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.22.0 <2.22.1

## Details
## Summary
In `BeanDeserializerBase.createContextual()`, per-property `@JsonIgnoreProperties` exclusions are applied by `_handleByNameInclusion()`, producing a `contextual` deserializer whose `BeanPropertyMap` has the ignored properties removed. The subsequent per-property case-insensitivity block (triggered by `@JsonFormat(ACCEPT_CASE_INSENSITIVE_PROPERTIES)`) rebuilds from `this._beanProperties` (the original, unfiltered map) instead of `contextual._beanProperties`, then overwrites the filtered map — restoring every property `_handleByNameInclusion` had just removed. The ignored property becomes writable again.

## Impact
An application that both enables case-insensitive matching and relies on per-property `@JsonIgnoreProperties` to keep a field unwritable can have that field set from untrusted JSON (mass-assignment-style write).

## Affected / Patched
Will be fixed in 2.18.9, 2.21.5, 2.22.1 and 3.1.4.

## Severity / CWE
Maintainer: minor. Reporter: Moderate. CWE-915.

## Upstream fix
FasterXML/jackson-databind#5962 (PR #5964, `0e1b0b2`), milestone 3.1.4. Released 2026-06-04.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-5jmj-h7xm-6q6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-54515
- https://github.com/FasterXML/jackson-databind/issues/5962
- https://github.com/FasterXML/jackson-databind/issues/5964
- https://github.com/FasterXML/jackson-databind/commit/0e1b0b211f7a53baa62ba2f4c9bd006c7bf4d5fa
- https://github.com/FasterXML/jackson-databind
