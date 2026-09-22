# [H] abomonation transmutes &T to and from &[u8] without sufficient constraints

## Summary
Severity: High
Advisory: GHSA-hfxp-p695-629x
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-hfxp-p695-629x
Type: github-advisory

## Affected
- crates.io: `abomonation` — affected >=0

## Details
This transmute is at the core of the abomonation crates. It's so easy to use it to violate alignment requirements that no test in the crate's test suite passes under miri.

The use of this transmute in serialization/deserialization also incorrectly assumes that the layout of a repr(Rust) type is stable.
This transmute can also disclose both the contents of padding bytes which may be an information leak and the contents of pointers, which may be used to defeat ASLR.

## References
- https://github.com/TimelyDataflow/abomonation/issues/23
- https://github.com/TimelyDataflow/abomonation
- https://rustsec.org/advisories/RUSTSEC-2021-0120.html
