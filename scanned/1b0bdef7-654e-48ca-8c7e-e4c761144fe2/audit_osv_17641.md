# [M] CVE-2020-18378

## Summary
Severity: Medium
Advisory: CVE-2020-18378
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-18378
Type: osv

## Details
A NULL pointer dereference was discovered in SExpressionWasmBuilder::makeBlock in wasm/wasm-s-parser.c in Binaryen 1.38.26. A crafted wasm input can cause a segmentation fault, leading to denial-of-service, as demonstrated by wasm-as.

## References
- https://github.com/WebAssembly/binaryen/issues/1900
