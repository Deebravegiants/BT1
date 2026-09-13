# [M] A vulnerability was detected in WebAssembly Binaryen up to 117. This issue affects the function...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1094
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/JLSEC-2026-1094
Type: osv

## Affected
- Julia: `Binaryen_jll` — affected >=0 <0.130.0+0

## Details
A vulnerability was detected in WebAssembly Binaryen up to 117. This issue affects the function IRBuilder::makeBrOn of the file src/wasm/wasm-ir-builder.cpp of the component BrOn Parser. Performing a manipulation results in reachable assertion. The attack needs to be approached locally. The exploit is now public and may be used. The patch is named 1251efbc1ea471c1311d2726b2bbe061ff2a291c. It is suggested to install a patch to address this issue.

## References
- https://github.com/HackC0der/CVE-Repos/blob/main/wasm-binaryen/Assertion_Failure_isRef_wasm_Type_getHeapType_commit_3ef8d19
- https://github.com/WebAssembly/binaryen
- https://github.com/WebAssembly/binaryen/
- https://github.com/WebAssembly/binaryen/commit/1251efbc1ea471c1311d2726b2bbe061ff2a291c
- https://github.com/WebAssembly/binaryen/issues/8633
- https://github.com/WebAssembly/binaryen/pull/8635
- https://github.com/advisories/GHSA-gmmj-chcc-2f2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-8257
- https://vuldb.com/submit/809552
- https://vuldb.com/vuln/362554
- https://vuldb.com/vuln/362554/cti
