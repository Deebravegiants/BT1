# [M] CVE-2019-7704

## Summary
Severity: Medium
Advisory: CVE-2019-7704
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7704
Type: osv

## Details
wasm::WasmBinaryBuilder::readUserSection in wasm-binary.cpp in Binaryen 1.38.22 triggers an attempt at excessive memory allocation, as demonstrated by wasm-merge and wasm-opt.

## References
- https://github.com/WebAssembly/binaryen/issues/1866
