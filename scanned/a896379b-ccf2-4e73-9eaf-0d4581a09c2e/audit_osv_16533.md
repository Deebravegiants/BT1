# [M] CVE-2019-7662

## Summary
Severity: Medium
Advisory: CVE-2019-7662
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-02-09
Source: https://osv.dev/vulnerability/CVE-2019-7662
Type: osv

## Details
An assertion failure was discovered in wasm::WasmBinaryBuilder::getType() in wasm-binary.cpp in Binaryen 1.38.22. This allows remote attackers to cause a denial of service (failed assertion and crash) via a crafted wasm file.

## References
- https://github.com/WebAssembly/binaryen/issues/1872
