# [M] CVE-2019-7703

## Summary
Severity: Medium
Advisory: CVE-2019-7703
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7703
Type: osv

## Details
In Binaryen 1.38.22, there is a use-after-free problem in wasm::WasmBinaryBuilder::visitCall in wasm-binary.cpp. Remote attackers could leverage this vulnerability to cause a denial-of-service via a wasm file, as demonstrated by wasm-merge.

## References
- https://github.com/WebAssembly/binaryen/issues/1865
