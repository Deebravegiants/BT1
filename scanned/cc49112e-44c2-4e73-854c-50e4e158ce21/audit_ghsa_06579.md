# [M] jackson-databind: @JsonIgnore on a Record property is bypassed with a PropertyNamingStrategy

## Summary
Severity: Medium
Advisory: GHSA-3pjw-73gf-8qr5
CVE: CVE-2026-59888
CWE: CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-3pjw-73gf-8qr5
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.15.0 <2.18.8
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
For Java Records, `POJOPropertiesCollector._removeUnwantedIgnorals()` records a `@JsonIgnore`-annotated component under its original implicit name before `_renameUsing()` applies the `PropertyNamingStrategy`. After the rename, `_ignoredPropertyNames` still holds only the pre-rename name, so `_ignorableProps` is built from the stale key. The renamed JSON key passes `IgnorePropertiesUtil.shouldIgnore()` and is assigned to the Record's constructor parameter, defeating the `@JsonIgnore`.

## Impact
A Record using a naming strategy that relies on `@JsonIgnore` to keep an internal/privileged component out of deserialization can have that component set from the wire via its renamed key (e.g. a role/flag controlled by an untrusted client).

## Affected / Patched (verified via `git tag --contains`)
- 2.15-2.18 line: `>= 2.15.0, < 2.18.8` -> fixed in **2.18.8** (backport `c7c6783`)
- 2.19-2.21 line: `>= 2.19.0, < 2.21.4` -> fixed in **2.21.4**
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4** (#5974, `baa2cdf`)

## Severity / CWE
Maintainer: minor. Reporter: Moderate. CWE-915; related CWE-345.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-3pjw-73gf-8qr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-59888
- https://github.com/FasterXML/jackson-databind/pull/5974
- https://github.com/FasterXML/jackson-databind/commit/baa2cdf5ca2b2717fbb88d91955d69d8651df3e4
- https://github.com/FasterXML/jackson-databind/commit/c7c678360624da5bc7eed2152789fa522880db9d
- https://github.com/FasterXML/jackson-databind
