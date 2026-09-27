# [M] CVE-2019-15758

## Summary
Severity: Medium
Advisory: CVE-2019-15758
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-15758
Type: osv

## Details
An issue was discovered in Binaryen 1.38.32. Missing validation rules in asmjs/asmangle.cpp can lead to an Assertion Failure at wasm/wasm.cpp in wasm::asmangle. A crafted input can cause denial-of-service, as demonstrated by wasm2js.

## References
- https://github.com/WebAssembly/binaryen/issues/2288
- https://github.com/WebAssembly/binaryen/pull/2290
