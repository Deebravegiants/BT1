# [M] fastify vulnerable to schema validation bypass via root primitive coercion mismatch

## Summary
Severity: Medium
Advisory: GHSA-w2qp-rph6-63g4
CVE: CVE-2026-18504
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-w2qp-rph6-63g4
Type: github-advisory

## Affected
- npm: `fastify` — affected >=0 <5.12.1

## Details
### Impact

`fastify` before 5.12.1, when a route uses a root-level primitive body schema (for example an integer with a minimum and maximum) and the default type coercion, validates the coerced value but exposes the original, uncoerced value to the route handler. For example, a JSON body `"10"` is coerced to the number `10` and passes an integer 1 to 10 schema, but `request.body` stays the string `"10"`. An application that trusts the validated type is handed a value that did not satisfy the schema, which can bypass limits the application enforces on that typed value. Object and array body schemas are not affected, they coerce their members in place.

### Patches

Upgrade to `fastify` 5.12.1.

### Workarounds

Until you can upgrade, avoid relying on the validated type of a root primitive body. Wrap the value in an object schema (object properties are coerced in place), for example accept `{ "value": 10 }` and read `request.body.value`, or re-check the type in the handler.

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-w2qp-rph6-63g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-18504
- https://github.com/fastify/fastify/commit/1ef8a60c87e94f42f666aa15ad68957772a83655
- https://cna.openjsf.org/security-advisories.html
- https://github.com/fastify/fastify
- https://github.com/fastify/fastify/releases/tag/v5.12.1
