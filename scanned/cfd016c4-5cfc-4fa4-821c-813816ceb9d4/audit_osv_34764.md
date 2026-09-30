# [M] WebAssembly Micro Runtime vulnerable to a segmentation fault in v128.store instruction

## Summary
Severity: Medium
Advisory: CVE-2025-64704
Aliases: GHSA-2f2p-wf5w-82qr
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-64704
Type: osv

## Details
WebAssembly Micro Runtime (WAMR) is a lightweight standalone WebAssembly (Wasm) runtime. Prior to version 2.4.4, WAMR is susceptible to a segmentation fault in v128.store instruction. This issue has been patched in version 2.4.4.

## References
- https://github.com/bytecodealliance/wasm-micro-runtime/releases/tag/WAMR-2.4.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64704.json
- https://github.com/bytecodealliance/wasm-micro-runtime/security/advisories/GHSA-2f2p-wf5w-82qr
- https://nvd.nist.gov/vuln/detail/CVE-2025-64704
