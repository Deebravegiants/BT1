# [M] CVE-2019-7700

## Summary
Severity: Medium
Advisory: CVE-2019-7700
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7700
Type: osv

## Details
A heap-based buffer over-read was discovered in wasm::WasmBinaryBuilder::visitCall in wasm-binary.cpp in Binaryen 1.38.22. A crafted wasm input can cause a segmentation fault, leading to denial-of-service, as demonstrated by wasm-merge.

## References
- https://github.com/WebAssembly/binaryen/issues/1864
