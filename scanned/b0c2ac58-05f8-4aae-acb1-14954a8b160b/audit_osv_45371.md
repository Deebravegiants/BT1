# [M] A vulnerability was identified in WebAssembly Binaryen up to 125. This affects the function...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1093
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1093
Type: osv

## Affected
- Julia: `Binaryen_jll` — affected >=0 <0.130.0+0

## Details
A vulnerability was identified in WebAssembly Binaryen up to 125. This affects the function IRBuilder::makeLocalGet/IRBuilder::makeLocalSet/IRBuilder::makeLocalTee of the file src/wasm/wasm-ir-builder.cpp of the component IRBuilder. Such manipulation of the argument Index leads to null pointer dereference. Local access is required to approach this attack. The exploit is publicly available and might be used. The name of the patch is 6fb2b917a79578ab44cf3b900a6da4c27251e0d4. Applying a patch is advised to resolve this issue.

## References
- https://github.com/WebAssembly/binaryen
- https://github.com/WebAssembly/binaryen/
- https://github.com/WebAssembly/binaryen/commit/6fb2b917a79578ab44cf3b900a6da4c27251e0d4
- https://github.com/WebAssembly/binaryen/issues/8090
- https://github.com/WebAssembly/binaryen/pull/8099
- https://github.com/advisories/GHSA-3h23-rfwm-gcx3
- https://github.com/oneafter/1204/blob/main/af1
- https://nvd.nist.gov/vuln/detail/CVE-2025-14957
- https://vuldb.com/?ctiid.337593
- https://vuldb.com/?id.337593
- https://vuldb.com/?submit.717317
- https://vuldb.com/?submit.717319
