# [M] ajv has ReDoS when using `$data` option

## Summary
Severity: Medium
Advisory: GHSA-2g4f-4pwh-qvx6
CVE: CVE-2025-69873
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
Type: github-advisory

## Affected
- npm: `ajv` — affected >=7.0.0-alpha.0 <8.18.0
- npm: `ajv` — affected >=0 <6.14.0

## Details
ajv (Another JSON Schema Validator) through version 8.17.1 is vulnerable to Regular Expression Denial of Service (ReDoS) when the `$data` option is enabled. The pattern keyword accepts runtime data via JSON Pointer syntax (`$data` reference), which is passed directly to the JavaScript `RegExp()` constructor without validation. An attacker can inject a malicious regex pattern (e.g., `\"^(a|a)*$\"`) combined with crafted input to cause catastrophic backtracking. A 31-character payload causes approximately 44 seconds of CPU blocking, with each additional character doubling execution time. This enables complete denial of service with a single HTTP request against any API using ajv with `$data`: true for dynamic schema validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-69873
- https://github.com/ajv-validator/ajv/pull/2586
- https://github.com/ajv-validator/ajv/pull/2588
- https://github.com/ajv-validator/ajv/pull/2590
- https://github.com/github/advisory-database/pull/6991
- https://github.com/ajv-validator/ajv/commit/720a23fa453ffae8340e92c9b0fe886c54cfe0d5
- https://github.com/EthanKim88/ethan-cve-disclosures/blob/main/CVE-2025-69873-ajv-ReDoS.md
- https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
- https://github.com/ajv-validator/ajv
- https://github.com/ajv-validator/ajv/releases/tag/v6.14.0
- https://github.com/ajv-validator/ajv/releases/tag/v8.18.0
