# [M] CSVTOJSON has a prototype pollution vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vrw9-g62v-7fmf
CVE: CVE-2025-57350
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-vrw9-g62v-7fmf
Type: github-advisory

## Affected
- npm: `csvtojson` — affected >=0 <2.0.13

## Details
The csvtojson package, a tool for converting CSV data to JSON with customizable parsing capabilities, contains a prototype pollution vulnerability in versions prior to 2.0.10. This issue arises due to insufficient sanitization of nested header names during the parsing process in the parser_jsonarray component. When processing CSV input containing specially crafted header fields that reference prototype chains (e.g., using __proto__ syntax), the application may unintentionally modify properties of the base Object prototype. This vulnerability can lead to denial of service conditions or unexpected behavior in applications relying on unmodified prototype chains, particularly when untrusted CSV data is processed. The flaw does not require user interaction beyond providing a maliciously constructed CSV file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57350
- https://github.com/Keyang/node-csvtojson/issues/498
- https://github.com/Keyang/node-csvtojson/issues/502
- https://github.com/Keyang/node-csvtojson/commit/4caeebd13b67be63282a7bbed3ca0cf9813f4bfc
- https://github.com/Keyang/node-csvtojson
- https://github.com/VulnSageAgent/PoCs/tree/main/JavaScript/prototype-pollution/CVE-2025-57350
- https://security.snyk.io/vuln/SNYK-JS-CSVTOJSON-13109616
