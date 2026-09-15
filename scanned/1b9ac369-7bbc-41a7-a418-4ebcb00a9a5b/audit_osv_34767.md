# [M] WebAssembly Micro Runtime frame_offset_bottom array bounds overflow in fast Interpreter mode when handling GET_GLOBAL(I32) followed by if opcode

## Summary
Severity: Medium
Advisory: CVE-2025-64713
Aliases: GHSA-gvx3-gg3x-rjcx
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-64713
Type: osv

## Details
WebAssembly Micro Runtime (WAMR) is a lightweight standalone WebAssembly (Wasm) runtime. Prior to version 2.4.4, an out-of-bounds array access issue exists in WAMR's fast interpreter mode during WASM bytecode loading. When frame_ref_bottom and frame_offset_bottom arrays are at capacity and a GET_GLOBAL(I32) opcode is encountered, frame_ref_bottom is expanded but frame_offset_bottom may not be. If this is immediately followed by an if opcode that triggers preserve_local_for_block, the function traverses arrays using stack_cell_num as the upper bound, causing out-of-bounds access to frame_offset_bottom since it wasn't expanded to match the increased stack_cell_num. This issue has been patched in version 2.4.4.

## References
- https://github.com/bytecodealliance/wasm-micro-runtime/releases/tag/WAMR-2.4.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64713.json
- https://github.com/bytecodealliance/wasm-micro-runtime/security/advisories/GHSA-gvx3-gg3x-rjcx
- https://nvd.nist.gov/vuln/detail/CVE-2025-64713
