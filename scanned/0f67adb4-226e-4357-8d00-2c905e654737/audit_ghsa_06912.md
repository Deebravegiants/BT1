# [H] fast-xml-parser: Repeated DOCTYPE declarations reset entity expansion limits

## Summary
Severity: High
Advisory: GHSA-8r6m-32jq-jx6q
CVE: CVE-2026-73569
CWE: CWE-776
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-8r6m-32jq-jx6q
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=5.9.3 <5.10.1

## Details
### Impact
`fast-xml-parser` processes multiple "DOCTYPE" declarations within a single XML document. Each declaration passes its entities to `@nodable/entities` through `addInputEntities()`.

`addInputEntities()` resets the entity expansion counters every time it is called. An attacker can therefore insert additional DOCTYPE declarations to repeatedly reset maxTotalExpansions and maxExpandedLength during one parse operation.

This allows a crafted XML document to exceed the configured entity-expansion limits and can cause excessive CPU use, event-loop blocking, memory exhaustion, and process termination.

### Workarounds
- Manually check if multiple DOCTYPEs are not present in input contents
- Update to v5.10.1
- Keep `processEntity` flag off

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-8r6m-32jq-jx6q
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/4e546e03987662de5495d050b5fba26bea65383f
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.10.1
