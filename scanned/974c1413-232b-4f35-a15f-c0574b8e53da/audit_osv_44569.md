# [H] fastify vulnerable to request validation bypass via skipped boolean false schemas

## Summary
Severity: High
Advisory: CVE-2026-84469
Aliases: GHSA-hwr6-493r-vm6h
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84469
Type: osv

## Details
fastify versions before 5.12.2 decide whether to compile a request schema based on JavaScript truthiness, but JSON Schema Draft 7 defines the boolean false as a valid schema that rejects every instance. When an application assigns false to a route's body, querystring, params, or headers schema to deny all input, fastify treats it as a missing schema, compiles no validator, and runs the route handler on any request. An unauthenticated remote client can therefore reach a handler that a valid deny-all schema was intended to make unreachable, a complete validation bypass that can lead to unauthorized state changes or execution of disabled operations. Users should upgrade to fastify 5.12.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84469.json
- https://github.com/fastify/fastify/security/advisories/GHSA-hwr6-493r-vm6h
- https://nvd.nist.gov/vuln/detail/CVE-2026-84469
