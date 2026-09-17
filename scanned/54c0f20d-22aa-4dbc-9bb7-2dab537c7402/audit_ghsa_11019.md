# [H] jackson-core has Nesting Depth Constraint Bypass in `UTF8DataInputJsonParser` potentially allowing Resource Exhaustion

## Summary
Severity: High
Advisory: GHSA-6v53-7c9g-w56r
CVE: CVE-2026-29062
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-6v53-7c9g-w56r
Type: github-advisory

## Affected
- Maven: `tools.jackson.core:jackson-core` — affected >=3.0.0 <3.1.0

## Details
### Summary
The `UTF8DataInputJsonParser`, which is used when parsing from a `java.io.DataInput` source, bypasses the `maxNestingDepth` constraint (default: 500) defined in `StreamReadConstraints`.

A similar issue was found in `ReaderBasedJsonParser`.

This allows a user to supply a JSON document with excessive nesting, which can cause a `StackOverflowError` when the structure is processed, leading to a Denial of Service (DoS).

The related fix for com.fasterxml.jackson.core:jackson-core, CVE-2025-52999, was not fully applied to tools.jackson.core:jackson-core until the 3.1.0 release. It is recommended that 3.0.x users upgrade.

### Patches
jackson-core contains a configurable limit for how deep Jackson will traverse in an input document. This check was missing in a few places in tools.jackson.core:jackson-core. 

The change is in https://github.com/FasterXML/jackson-core/pull/1554. jackson-core will throw a StreamConstraintsException if the limit is reached.

jackson-databind also benefits from this change because it uses jackson-core to parse JSON inputs.

### Workarounds
Users should avoid parsing input files from untrusted sources.

### Resources
[GHSA-6v53-7c9g-w56r](https://github.com/FasterXML/jackson-core/security/advisories/GHSA-6v53-7c9g-w56r)
https://nvd.nist.gov/vuln/detail/CVE-2025-52999
https://github.com/FasterXML/jackson-core/pull/1554

## References
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-6v53-7c9g-w56r
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-h46c-h94j-95f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-52999
- https://nvd.nist.gov/vuln/detail/CVE-2026-29062
- https://github.com/FasterXML/jackson-core/pull/1554
- https://github.com/FasterXML/jackson-core/commit/8b25fd67f20583e75fb09564ce1eaab06cd5a902
- https://github.com/FasterXML/jackson-core
