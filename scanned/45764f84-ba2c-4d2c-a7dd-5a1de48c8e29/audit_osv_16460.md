# [M] CVE-2019-7154

## Summary
Severity: Medium
Advisory: CVE-2019-7154
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-7154
Type: osv

## Details
The main function in tools/wasm2js.cpp in Binaryen 1.38.22 has a heap-based buffer overflow because Emscripten is misused, triggering an error in cashew::JSPrinter::printAst() in emscripten-optimizer/simple_ast.h. A crafted input can cause segmentation faults, leading to denial-of-service, as demonstrated by wasm2js.

## References
- https://github.com/WebAssembly/binaryen/issues/1876
