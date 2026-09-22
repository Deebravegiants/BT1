# [H] CVE-2024-34251

## Summary
Severity: High
Advisory: CVE-2024-34251
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-34251
Type: osv

## Details
An out-of-bound memory read vulnerability was discovered in Bytecode Alliance wasm-micro-runtime v2.0.0 which allows a remote attacker to cause a denial of service via the "block_type_get_arity" function in core/iwasm/interpreter/wasm.h.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34251.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34251
- https://github.com/bytecodealliance/wasm-micro-runtime/issues/3347
