# [M] CVE-2019-7152

## Summary
Severity: Medium
Advisory: CVE-2019-7152
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7152
Type: osv

## Details
A heap-based buffer over-read was discovered in wasm::WasmBinaryBuilder::processFunctions() in wasm/wasm-binary.cpp (when calling wasm::WasmBinaryBuilder::getFunctionIndexName) in Binaryen 1.38.22. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by wasm-opt.

## References
- https://github.com/WebAssembly/binaryen/issues/1880
