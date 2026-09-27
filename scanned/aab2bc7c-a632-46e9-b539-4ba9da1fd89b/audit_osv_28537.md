# [M] CVE-2024-34250

## Summary
Severity: Medium
Advisory: CVE-2024-34250
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-06
Source: https://osv.dev/vulnerability/CVE-2024-34250
Type: osv

## Details
A heap buffer overflow vulnerability was discovered in Bytecode Alliance wasm-micro-runtime v2.0.0 which allows a remote attacker to cause at least a denial of service via the "wasm_loader_check_br" function in core/iwasm/interpreter/wasm_loader.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34250.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34250
- https://github.com/bytecodealliance/wasm-micro-runtime/issues/3346
