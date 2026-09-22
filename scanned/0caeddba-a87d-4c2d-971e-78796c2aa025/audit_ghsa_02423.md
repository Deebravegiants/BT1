# [C] Out of bounds access in rgb

## Summary
Severity: Critical
Advisory: GHSA-g4rw-8m5q-6453
CVE: CVE-2020-25016
CWE: CWE-119, CWE-843
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g4rw-8m5q-6453
Type: github-advisory

## Affected
- crates.io: `rgb` — affected >=0.5.4 <0.8.20

## Details
Affected versions of rgb crate allow viewing and modifying data of any type T wrapped in RGB<T> as bytes, and do not correctly constrain RGB<T> and other wrapper structures to the types for which it is safe to do so.

Safety violation possible for a type wrapped in RGB<T> and similar wrapper structures:

* If T contains padding, viewing it as bytes may lead to exposure of contents of uninitialized memory.
* If T contains a pointer, modifying it as bytes may lead to dereferencing of arbitrary pointers.
* Any safety and/or validity invariants for T may be violated.

The issue was resolved by requiring all types wrapped in structures provided by RGB crate to implement an unsafe marker trait.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25016
- https://github.com/kornelski/rust-rgb/issues/35
- https://github.com/kornelski/rust-rgb
- https://rustsec.org/advisories/RUSTSEC-2020-0029.html
