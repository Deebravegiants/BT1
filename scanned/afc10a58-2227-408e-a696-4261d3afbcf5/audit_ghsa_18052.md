# [M] User-defined implementations of the safe trait scratchpad::Tracking can cause heap buffer overflows

## Summary
Severity: Medium
Advisory: GHSA-77h3-w9rx-hj3q
CWE: CWE-122
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-77h3-w9rx-hj3q
Type: github-advisory

## Affected
- crates.io: `scratchpad` — affected >=0

## Details
The `get` and `set` methods of the public trait `scratchpad::Tracking` interact with unsafe code regions in the crate, and they influence the computation of addresses returned as raw pointers. However, the trait itself is not marked as unsafe, meaning users may provide custom implementations under the assumption that the crate upholds all safety guarantees.

This becomes problematic because even safe implementations of `get` and `set`-written without using any unsafe code-can still result in ill-formed raw pointers. These pointers may later be dereferenced within safe APIs of the crate (e.g., `marker::MarkerBack::allocate_slice_copy`), potentially leading to arbitrary memory access or heap buffer overflows.

According to the [penultimate commit](https://github.com/okready/scratchpad/commit/957dee1a3902f48600b06910e8e0b1d5ee7dab83), the crate is in maintenance mode awaiting a cleanup that will reduce the area of unsafe code. Note that the last commits to the repository are from 4 years ago.

## References
- https://github.com/okready/scratchpad/issues/2
- https://github.com/okready/scratchpad
- https://rustsec.org/advisories/RUSTSEC-2025-0049.html
