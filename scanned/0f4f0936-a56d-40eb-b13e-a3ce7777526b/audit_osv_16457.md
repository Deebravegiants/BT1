# [M] CVE-2019-7151

## Summary
Severity: Medium
Advisory: CVE-2019-7151
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7151
Type: osv

## Details
A NULL pointer dereference was discovered in wasm::Module::getFunctionOrNull in wasm/wasm.cpp in Binaryen 1.38.22. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by wasm-opt.

## References
- https://github.com/WebAssembly/binaryen/issues/1881
