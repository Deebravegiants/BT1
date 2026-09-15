# [M] CVE-2021-46054

## Summary
Severity: Medium
Advisory: CVE-2021-46054
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2021-46054
Type: osv

## Details
A Denial of Service vulnerability exists in Binaryen 104 due to an assertion abort in wasm::WasmBinaryBuilder::visitRethrow(wasm::Rethrow*).

## References
- https://github.com/WebAssembly/binaryen/issues/4410
