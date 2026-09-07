# [M] jackson-databind's renamed @JsonIgnore'd setters can deserialize via private fields

## Summary
Severity: Medium
Advisory: GHSA-9fxm-vc8v-hj55
CVE: CVE-2026-54516
CWE: CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-9fxm-vc8v-hj55
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.21.0 <2.21.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
`POJOPropertiesCollector._renameProperties()` allows a property with `@JsonProperty("renamed")` on the getter and `@JsonIgnore` on the setter to be renamed rather than dropped. With `MapperFeature.INFER_PROPERTY_MUTATORS` enabled (default), the private backing field is retained; during deserialization `BeanDeserializerFactory.addBeanProps()` sees `hasField()==true`, builds a `FieldProperty`, and makes the backing field writable. An attacker supplying the renamed JSON key writes the backing field directly, bypassing the `@JsonIgnore` on the setter.

## Impact
POJOs combining a renamed getter with an ignored setter (a read-only-over-the-wire pattern) have that field silently set from attacker input (property tampering / mass assignment). Not a general gadget; no RCE.

## Affected / Patched (verified via `git tag --contains`)
- 2.21 line: `>= 2.21.0, < 2.21.4` -> fixed in **2.21.4** (backport `c3d56dd`, #5968)
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5967, `e88cb17`)

## Severity / CWE
Maintainer: minor. Reporter: HIGH. CWE-915.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-9fxm-vc8v-hj55
- https://nvd.nist.gov/vuln/detail/CVE-2026-54516
- https://github.com/FasterXML/jackson-databind/pull/5967
- https://github.com/FasterXML/jackson-databind/pull/5968
- https://github.com/FasterXML/jackson-databind/commit/c3d56dd25d52319828147c5b9aeabf2d485c250a
- https://github.com/FasterXML/jackson-databind/commit/e88cb17006b6af4883b973058f0bb6486e5074af
- https://github.com/FasterXML/jackson-databind
