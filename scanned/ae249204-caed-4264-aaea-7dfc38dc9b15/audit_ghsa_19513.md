# [M] jsonschema2pojo has Improper Restriction of Operations within the Bounds of a Memory Buffer

## Summary
Severity: Medium
Advisory: GHSA-66rc-vg9f-48m7
CVE: CVE-2025-3588
CWE: CWE-119
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-66rc-vg9f-48m7
Type: github-advisory

## Affected
- Maven: `org.jsonschema2pojo:jsonschema2pojo-core` — affected >=0

## Details
A vulnerability, which was classified as problematic, has been found in joelittlejohn jsonschema2pojo 1.2.2. This issue affects the function apply of the file org/jsonschema2pojo/rules/SchemaRule.java of the component JSON File Handler. The manipulation leads to stack-based buffer overflow. Attacking locally is a requirement. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3588
- https://github.com/joelittlejohn/jsonschema2pojo/issues/1672
- https://github.com/joelittlejohn/jsonschema2pojo
- https://vuldb.com/?ctiid.304643
- https://vuldb.com/?id.304643
- https://vuldb.com/?submit.550136
