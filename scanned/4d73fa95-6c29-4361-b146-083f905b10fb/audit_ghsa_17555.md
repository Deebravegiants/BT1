# [H] jackson-core can throw a StackoverflowError when processing deeply nested data

## Summary
Severity: High
Advisory: GHSA-h46c-h94j-95f3
CVE: CVE-2025-52999
CWE: CWE-121
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-27
Source: https://github.com/advisories/GHSA-h46c-h94j-95f3
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-core` — affected >=0 <2.15.0

## Details
### Impact
With older versions  of jackson-core, if you parse an input file and it has deeply nested data, Jackson could end up throwing a StackoverflowError if the depth is particularly large.

### Patches
jackson-core 2.15.0 contains a configurable limit for how deep Jackson will traverse in an input document, defaulting to an allowable depth of 1000. Change is in https://github.com/FasterXML/jackson-core/pull/943. jackson-core will throw a StreamConstraintsException if the limit is reached.
jackson-databind also benefits from this change because it uses jackson-core to parse JSON inputs.

### Workarounds
Users should avoid parsing input files from untrusted sources.

## References
- https://github.com/FasterXML/jackson-core/security/advisories/GHSA-h46c-h94j-95f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-52999
- https://github.com/FasterXML/jackson-core/pull/943
- https://github.com/FasterXML/jackson-core
