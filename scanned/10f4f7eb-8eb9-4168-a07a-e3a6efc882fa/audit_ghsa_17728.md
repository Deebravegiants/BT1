# [M] fast-float2 has a segmentation fault due to lack of bound check

## Summary
Severity: Medium
Advisory: GHSA-jqcp-xc3v-f446
Ecosystem: crates.io
Published: 2025-01-29
Source: https://github.com/advisories/GHSA-jqcp-xc3v-f446
Type: github-advisory

## Affected
- crates.io: `fast-float2` — affected >=0 <0.2.2

## Details
In this case, the "fast_float2::common::AsciiStr::first" method within the "AsciiStr" struct 
uses the unsafe keyword to reading from memory without performing bounds checking. 
Specifically, it directly dereferences a pointer offset by "self.ptr".
Because of the above reason, the method accesses invalid memory address when it takes an empty string as its input.
This approach violates Rust’s memory safety guarantees, as it can lead to invalid memory access if empty buffer is provided.

## References
- https://github.com/aldanor/fast-float-rust/issues/38
- https://github.com/Alexhuszagh/fast-float-rust/pull/7
- https://github.com/Alexhuszagh/fast-float-rust
- https://rustsec.org/advisories/RUSTSEC-2025-0002.html
