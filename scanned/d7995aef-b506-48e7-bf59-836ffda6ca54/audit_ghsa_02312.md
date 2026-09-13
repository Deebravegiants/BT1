# [M] Data races in generator

## Summary
Severity: Medium
Advisory: GHSA-w3g5-2848-2v8r
CVE: CVE-2020-36471
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w3g5-2848-2v8r
Type: github-advisory

## Affected
- crates.io: `generator` — affected >=0 <0.7.0

## Details
The `Generator` type is an iterable which uses a generator function that yields
values. In affected versions of the crate, the provided function yielding values
had no `Send` bounds despite the `Generator` itself implementing `Send`.

The generator function lacking a `Send` bound means that types that are
dangerous to send across threads such as `Rc` could be sent as part of a
generator, potentially leading to data races.

This flaw was fixed in commit [`f7d120a3b`](https://github.com/Xudong-Huang/generator-rs/commit/f7d120a3b724d06a7b623d0a4306acf8f78cb4f0)
by enforcing that the generator function be bound by `Send`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36471
- https://github.com/Xudong-Huang/generator-rs/issues/27
- https://github.com/Xudong-Huang/generator-rs/commit/f7d120a3b724d06a7b623d0a4306acf8f78cb4f0
- https://github.com/Xudong-Huang/generator-rs
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/generator/RUSTSEC-2020-0151.md
- https://rustsec.org/advisories/RUSTSEC-2020-0151.html
