# [M] BIT-node-2023-39333

## Summary
Severity: Medium
Advisory: BIT-node-2023-39333
Aliases: BIT-node-min-2023-39333, CVE-2023-39333
Ecosystem: Bitnami
Published: 2024-09-10
Source: https://osv.dev/vulnerability/BIT-node-2023-39333
Type: osv

## Affected
- Bitnami: `node` — affected >=19.0.0 <20.8.1

## Details
Maliciously crafted export names in an imported WebAssembly module can inject JavaScript code. The injected code may be able to access data and functions that the WebAssembly module itself does not have access to, similar to as if the WebAssembly module was a JavaScript module.

This vulnerability affects users of any active release line of Node.js. The vulnerable feature is only available if Node.js is started with the `--experimental-wasm-modules` command line option.

## References
- https://nodejs.org/en/blog/vulnerability/october-2023-security-releases
- https://security.netapp.com/advisory/ntap-20240808-0004/
- https://security.netapp.com/advisory/ntap-20241004-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39333
- https://security.netapp.com/advisory/ntap-20241108-0002/
