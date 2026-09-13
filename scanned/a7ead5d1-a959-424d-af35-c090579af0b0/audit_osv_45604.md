# [M] JLSEC-2026-1368

## Summary
Severity: Medium
Advisory: JLSEC-2026-1368
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/JLSEC-2026-1368
Type: osv

## Affected
- Julia: `Wasmtime_jll` — affected >=0 <46.0.1+0

## Details
Wasmtime is a runtime for WebAssembly. Prior to 24.0.11, 36.0.12, 45.0.3, and 46.0.1, wasmtime-wasi hard-link creation and renaming check directory permissions but not matching FilePerms on source and destination preopens, allowing a WASI guest with a read-only source file capability to overwrite host files exposed as FilePerms::READ through wasip1, wasip2, or wasip3 filesystem interfaces. This issue is fixed in versions 24.0.11, 36.0.12, 45.0.3, and 46.0.1.

## References
- https://github.com/bytecodealliance/wasmtime/commit/5ddfd5f1ef28f2041fa07d237ad0336e167b0e0c
- https://github.com/bytecodealliance/wasmtime/commit/7db94cdcf0c79cb3dfde884b534b653f2dd83367
- https://github.com/bytecodealliance/wasmtime/commit/8a250aac0962ca1364b5f16525720e9d0b39edcd
- https://github.com/bytecodealliance/wasmtime/commit/d3ceb56ec35f39e02496eeb4e2d9c7f4fb964d9e
- https://github.com/bytecodealliance/wasmtime/releases/tag/v24.0.11
- https://github.com/bytecodealliance/wasmtime/releases/tag/v36.0.12
- https://github.com/bytecodealliance/wasmtime/releases/tag/v45.0.3
- https://github.com/bytecodealliance/wasmtime/releases/tag/v46.0.1
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-4ch3-9j33-3pmj
