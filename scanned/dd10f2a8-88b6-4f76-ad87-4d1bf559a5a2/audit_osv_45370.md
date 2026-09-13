# [H] A vulnerability was determined in WebAssembly Binaryen up to 125. Affected by this issue is the...

## Summary
Severity: High
Advisory: JLSEC-2026-1092
Ecosystem: Julia
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1092
Type: osv

## Affected
- Julia: `Binaryen_jll` — affected >=0 <0.130.0+0

## Details
A vulnerability was determined in WebAssembly Binaryen up to 125. Affected by this issue is the function WasmBinaryReader::readExport of the file src/wasm/wasm-binary.cpp. This manipulation causes heap-based buffer overflow. It is possible to launch the attack on the local host. The exploit has been publicly disclosed and may be utilized. Patch name: 4f52bff8c4075b5630422f902dd92a0af2c9f398. It is recommended to apply a patch to fix this issue.

## References
- https://github.com/WebAssembly/binaryen
- https://github.com/WebAssembly/binaryen/
- https://github.com/WebAssembly/binaryen/commit/4f52bff8c4075b5630422f902dd92a0af2c9f398
- https://github.com/WebAssembly/binaryen/issues/8089
- https://github.com/WebAssembly/binaryen/pull/8092
- https://github.com/advisories/GHSA-vjgx-vcpf-hm6w
- https://github.com/oneafter/1204/blob/main/hbf
- https://nvd.nist.gov/vuln/detail/CVE-2025-14956
- https://vuldb.com/?ctiid.337592
- https://vuldb.com/?id.337592
- https://vuldb.com/?submit.717315
