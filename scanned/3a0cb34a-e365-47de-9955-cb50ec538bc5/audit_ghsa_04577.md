# [M] jackson-databind: Deeply nested JsonNode throws StackOverflowError for toString()

## Summary
Severity: Medium
Advisory: GHSA-3wrr-7qpf-2prh
CVE: CVE-2026-50193
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-3wrr-7qpf-2prh
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.10.0 <2.14.0

## Details
### Impact

Potential Denial-of-Service when attacker sends deeply nested JSON if (and only if) service:

1. Reads deeply nested (1000s of levels) JSON as `JsonNode` (ObjectMapper.readTree())
2. Writes out same (or modifided) node using `JsonNode.toString()`

which can consume significant amount of resources with concurrent relatively small requests (1000 nested arrays is 2kB).

### Patches

Fixed in 2.14.0 via https://github.com/FasterXML/jackson-databind/issues/3447.

### Workarounds

Avoid serializing `JsonNode` using `toString()`: use ObjectMapper.writeValueAsString(node)

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-3wrr-7qpf-2prh
- https://nvd.nist.gov/vuln/detail/CVE-2026-50193
- https://github.com/FasterXML/jackson-databind/issues/3447
- https://github.com/FasterXML/jackson-databind/commit/a1fa4ae4ecf5cee16da465985f135f3e81816f8c
- https://github.com/FasterXML/jackson-databind
