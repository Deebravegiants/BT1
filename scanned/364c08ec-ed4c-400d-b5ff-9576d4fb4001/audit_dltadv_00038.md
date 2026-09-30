# [M] Excessive number of function parameters in compiled Wasm in github.com/CosmWasm/wasmvm

## Summary
Severity: Medium
Advisory: GO-2024-3101
Aliases: GHSA-75qh-gg76-p2w4, RUSTSEC-2024-0366
Package: github.com/CosmWasm/wasmvm
Published: 2024-12-20
Source: https://osv.dev/vulnerability/GO-2024-3101
Type: chain-advisory

## Affected
- Go: `github.com/CosmWasm/wasmvm` — affected >=1.5.0 <1.5.1

## Details
A specifically crafted Wasm file can cause the VM to consume excessive amounts of memory when compiling a contract. This can lead to high memory usage, slowdowns, potentially a crash and can poison a lock in the VM, preventing any further interaction with contracts.

## References
- https://github.com/advisories/GHSA-75qh-gg76-p2w4
- https://forum.cosmos.network/t/high-severity-security-patch-upcoming-on-wed-10th-cwa-2023-004-brought-to-you-by-certik-and-confio/12840
- https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-004.md
- https://rustsec.org/advisories/RUSTSEC-2024-0366.html
- https://www.certik.com/resources/blog/risk-and-security-enhancement-for-app-chains-an-in-depth-writeup-of-cwa-2023
