# [M] CVE-2019-7702

## Summary
Severity: Medium
Advisory: CVE-2019-7702
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-10
Source: https://osv.dev/vulnerability/CVE-2019-7702
Type: osv

## Details
A NULL pointer dereference was discovered in wasm::SExpressionWasmBuilder::parseExpression in wasm-s-parser.cpp in Binaryen 1.38.22. A crafted wasm input can cause a segmentation fault, leading to denial-of-service, as demonstrated by wasm-as.

## References
- https://github.com/WebAssembly/binaryen/issues/1867
