# [C] Use after free in image

## Summary
Severity: Critical
Advisory: GHSA-m2pf-hprp-3vqm
CVE: CVE-2019-16138
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m2pf-hprp-3vqm
Type: github-advisory

## Affected
- crates.io: `image` — affected >=0.10.2 <0.21.3

## Details
Affected versions of this crate would call Vec::set_len on an uninitialized vector with user-provided type parameter, in an interface of the HDR image format decoder. They would then also call other code that could panic before initializing all instances.

This could run Drop implementations on uninitialized types, equivalent to use-after-free, and allow an attacker arbitrary code execution.

Two different fixes were applied. It is possible to conserve the interface by ensuring proper initialization before calling Vec::set_len. Drop is no longer called in case of panic, though.

Starting from version 0.22, a breaking change to the interface requires callers to pre-allocate the output buffer and pass a mutable slice instead, avoiding all unsafe code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16138
- https://github.com/image-rs/image/pull/985
- https://github.com/image-rs/image
- https://rustsec.org/advisories/RUSTSEC-2019-0014.html
