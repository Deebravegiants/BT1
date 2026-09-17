# [C] Orval: RCE via schema property name -> computed-property-key injection in the MSW mock generator

## Summary
Severity: Critical
Advisory: CVE-2026-71867
Aliases: GHSA-2w86-xfrc-g85r
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-71867
Type: osv

## Details
Orval generates type-safe JavaScript clients in TypeScript from OpenAPI v3 and Swagger v2 specifications. Prior to 8.21.0, a single quote in a schema property name is emitted into single-quoted object keys in generated MSW mock factories without safe encoding. This permits attacker-controlled JavaScript to be evaluated when the generated mock factory is called by tests or an MSW handler, resulting in code execution in the developer, CI, test, or application environment. The affected code is packages/core/src/getters/keys.ts function getKey and MSW mock generation. This issue is fixed in version 8.21.0.

## References
- https://github.com/orval-labs/orval/releases/tag/v8.21.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71867.json
- https://github.com/orval-labs/orval/security/advisories/GHSA-2w86-xfrc-g85r
- https://nvd.nist.gov/vuln/detail/CVE-2026-71867
- https://github.com/orval-labs/orval/commit/8ef1bfdf3f9bcaf9dabfbe2e42887f1c0e159ab6
- https://github.com/orval-labs/orval/pull/3692
