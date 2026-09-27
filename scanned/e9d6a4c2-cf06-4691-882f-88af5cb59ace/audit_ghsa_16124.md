# [M] Mimalloc Can Allocate Memory with Bad Alignment

## Summary
Severity: Medium
Advisory: GHSA-g23h-7vf9-xc25
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-g23h-7vf9-xc25
Type: github-advisory

## Affected
- crates.io: `mimalloc` — affected >=0 <0.1.39

## Details
This crate depended on a promise regarding alignments made by the author of the mimalloc allocator to avoid using aligned allocation functions where possible for performance reasons.
Since then, the mimalloc allocator's logic changed, making it break this promise.
This caused this crate to return memory with an incorrect alignment for some allocations, particularly those with large alignments.
The flaw was fixed by always using the aligned allocation functions.

## References
- https://github.com/purpleprotocol/mimalloc_rust/issues/87
- https://github.com/purpleprotocol/mimalloc_rust
- https://rustsec.org/advisories/RUSTSEC-2022-0094.html
