# [H] fastify vulnerable to request body replacement via an async validation result collision

## Summary
Severity: High
Advisory: CVE-2026-84504
Aliases: GHSA-667r-xxjv-c9mm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-84504
Type: osv

## Details
fastify versions before 5.12.2 treat the object resolved by a successful Ajv async validator as the value result protocol used by custom validator compilers. If a request that passes its route schema contains a property named value at the root, fastify replaces the entire request body with that property's value before the handler runs, so the handler receives a different object than the one that satisfied the schema. An authenticated low-privilege caller can use this to make nested data replace the validated body and trigger an operation the route schema did not authorize, leading to unauthorized state changes and data disclosure. Users should upgrade to fastify 5.12.2 or later.

## References
- https://cna.openjsf.org/security-advisories.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84504.json
- https://github.com/fastify/fastify/security/advisories/GHSA-667r-xxjv-c9mm
- https://nvd.nist.gov/vuln/detail/CVE-2026-84504
