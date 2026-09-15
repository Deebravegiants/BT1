# [H] serde-json-wasm stack overflow during recursive JSON parsing

## Summary
Severity: High
Advisory: GHSA-rr69-rxr6-8qwf
CVE: CVE-2024-58264
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-rr69-rxr6-8qwf
Type: github-advisory

## Affected
- crates.io: `serde-json-wasm` — affected >=1.0.0 <1.0.1
- crates.io: `serde-json-wasm` — affected >=0 <0.5.2

## Details
When parsing untrusted, deeply nested JSON, the stack may overflow, possibly enabling a Denial of Service attack. This was fixed by adding a check for recursion depth.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-58264
- https://github.com/CosmWasm/serde-json-wasm/commit/a9a9b9bf243862bd2afbf6853fca97f30dc4f620
- https://github.com/CosmWasm/serde-json-wasm/commit/e78f9e28b3a2151d3175ee88ab2a001bf9515429
- https://github.com/CosmWasm/serde-json-wasm
- https://rustsec.org/advisories/RUSTSEC-2024-0012.html
