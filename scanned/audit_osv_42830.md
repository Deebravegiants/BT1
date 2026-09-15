# [C] Orval: Import-time RCE via enum-typed default -> zod module-level template literal

## Summary
Severity: Critical
Advisory: CVE-2026-71868
Aliases: GHSA-3575-w9fc-c2j6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-71868
Type: osv

## Details
Orval generates type-safe JavaScript clients in TypeScript from OpenAPI v3 and Swagger v2 specifications. Prior to 8.21.0, a ${...} expression or backtick in an enum default is emitted into a module-level template literal emitted by zod schema generation without safe encoding. This permits attacker-controlled JavaScript to be evaluated when the generated zod schema module is imported, resulting in code execution in the developer, CI, test, or application environment. The affected code is packages/zod/src/index.ts function formatDefaultValue. This issue is fixed in version 8.21.0.

## References
- https://github.com/orval-labs/orval/releases/tag/v8.21.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71868.json
- https://github.com/orval-labs/orval/security/advisories/GHSA-3575-w9fc-c2j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-71868
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval/pull/3692
