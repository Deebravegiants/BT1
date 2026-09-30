# [H] jackson-databind has an array subtype allowlist bypass in BasicPolymorphicTypeValidator (allowIfSubTypeIsArray)

## Summary
Severity: High
Advisory: GHSA-rmj7-2vxq-3g9f
CVE: CVE-2026-54513
CWE: CWE-184
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-rmj7-2vxq-3g9f
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.10.0 <2.18.8
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
## Summary
`BasicPolymorphicTypeValidator.Builder.allowIfSubTypeIsArray()` allowlists any array type based only on `clazz.isArray()`, without validating the array's component (element) type against the configured allowlist. A PTV built with `allowIfSubTypeIsArray()` plus an explicit concrete-type allowlist therefore still permits `EvilType[]` even though `EvilType` is not allowlisted. When Jackson deserializes the elements and no per-element type IDs are present, it instantiates the component type directly with no further PTV check, bypassing the allowlist.

## Impact
Applications using `BasicPolymorphicTypeValidator` with `allowIfSubTypeIsArray()` as a safeguard get no protection for concrete array component types; an attacker controlling JSON can instantiate non-allowlisted types via an array wrapper, re-opening the gadget-instantiation risk PTV is meant to prevent.

## Affected / Patched (verified via `git tag --contains`)
- 2.18 line: `>= 2.10.0, < 2.18.8` -> fixed in **2.18.8**
- 2.19-2.21 line: `>= 2.19.0, < 2.21.4` -> fixed in **2.21.4**
- 3.x line: `>= 3.0.0, < 3.1.4` -> fixed in **3.1.4**

`PolymorphicTypeValidator` was added in 2.10.0 so vulnerability N/A for versions prior to that.

## Severity / CWE
Maintainer: significant. Reporter: HIGH. CWE-184 (Incomplete List of Disallowed Inputs); related CWE-502.

## Upstream fix
FasterXML/jackson-databind#5981; fix PR #5983 (`24529da`), 2.18 backport PR #5984 (`01d1692`). Released 2026-06-04 in 2.18.8 / 2.21.4 / 3.1.4.

## Credits
Omkhar Arasaratnam (@omkhar) - finder.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-rmj7-2vxq-3g9f
- https://nvd.nist.gov/vuln/detail/CVE-2026-54513
- https://github.com/FasterXML/jackson-databind/issues/5983
- https://github.com/FasterXML/jackson-databind/issues/5981
- https://github.com/FasterXML/jackson-databind/pull/5984
- https://github.com/FasterXML/jackson-databind/commit/24529da29fdf46ff94ca38de9ebf31cd188f5e8e
- https://github.com/FasterXML/jackson-databind/commit/01d1692c8d0ed03e51a0e3c4f8a9e6908e4931e5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-54513.json
- https://github.com/FasterXML/jackson-databind
- https://bugzilla.redhat.com/show_bug.cgi?id=2492010
- https://access.redhat.com/security/cve/CVE-2026-54513
- https://access.redhat.com/errata/RHSA-2026:62260
- https://access.redhat.com/errata/RHSA-2026:54622
- https://access.redhat.com/errata/RHSA-2026:54435
- https://access.redhat.com/errata/RHSA-2026:50849
- https://access.redhat.com/errata/RHSA-2026:50848
- https://access.redhat.com/errata/RHSA-2026:50847
- https://access.redhat.com/errata/RHSA-2026:50846
- https://access.redhat.com/errata/RHSA-2026:48151
- https://access.redhat.com/errata/RHSA-2026:48095
