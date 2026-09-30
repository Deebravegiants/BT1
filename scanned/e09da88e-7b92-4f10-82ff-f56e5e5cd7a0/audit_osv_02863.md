# [M] ALPINE-CVE-2023-39333

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-39333
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-09-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-39333
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.18.2-r0

## Details
Maliciously crafted export names in an imported WebAssembly module can inject JavaScript code. The injected code may be able to access data and functions that the WebAssembly module itself does not have access to, similar to as if the WebAssembly module was a JavaScript module.

This vulnerability affects users of any active release line of Node.js. The vulnerable feature is only available if Node.js is started with the `--experimental-wasm-modules` command line option.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-39333
