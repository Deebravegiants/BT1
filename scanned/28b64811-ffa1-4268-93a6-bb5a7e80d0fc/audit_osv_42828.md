# [C] Orval: Import-time RCE via query parameter name -> computed-property-key injection in the zod cli

## Summary
Severity: Critical
Advisory: CVE-2026-71865
Aliases: GHSA-653q-5476-x79g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-71865
Type: osv

## Details
Orval generates type-safe JavaScript clients in TypeScript from OpenAPI v3 and Swagger v2 specifications. Prior to 8.21.0, a double quote in a query parameter name is emitted into the generated request-validation zod.object({...}) schema without safe encoding. This permits attacker-controlled JavaScript to be evaluated when the generated zod schema module is imported, resulting in code execution in the developer, CI, test, or application environment. The affected code is packages/zod/src/index.ts and query request-validation generation. This issue is fixed in version 8.21.0.

## References
- https://github.com/orval-labs/orval/releases/tag/v8.21.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71865.json
- https://github.com/orval-labs/orval/security/advisories/GHSA-653q-5476-x79g
- https://nvd.nist.gov/vuln/detail/CVE-2026-71865
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval/pull/3692
