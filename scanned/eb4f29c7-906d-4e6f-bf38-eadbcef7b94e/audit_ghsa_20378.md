# [M] Panic on incorrect date input to `simple_asn1`

## Summary
Severity: Medium
Advisory: GHSA-3m6f-3gfg-4x56
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-3m6f-3gfg-4x56
Type: github-advisory

## Affected
- crates.io: `simple_asn1` — affected >=0.6.0 <0.6.1

## Details
Version 0.6.0 of the `simple_asn1` crate panics on certain malformed
inputs to its parsing functions, including `from_der` and `der_decode`.
Because this crate is frequently used with inputs from the network, this
should be considered a security vulnerability.

The issue occurs when parsing the old ASN.1 "UTCTime" time format.  If an
attacker provides a UTCTime where the first character is ASCII but the
second character is above 0x7f, a string slice operation in the
`from_der_` function will try to slice into the middle of a UTF-8
character, and cause a panic.

This error was introduced in commit
[`d7d39d709577710e9dc8`](https://github.com/acw/simple_asn1/commit/d7d39d709577710e9dc8833ee57d200eef366db8),
which updated `simple_asn1` to use `time` instead of `chrono` because of
[`RUSTSEC-2020-159`](https://rustsec.org/advisories/RUSTSEC-2020-0159).
Versions of `simple_asn1` before 0.6.0 are not affected by this issue.

The [patch](https://github.com/acw/simple_asn1/pull/28) was applied in
`simple_asn1` version 0.6.1.

## References
- https://github.com/acw/simple_asn1/issues/27
- https://github.com/acw/simple_asn1/commit/d7d39d709577710e9dc8833ee57d200eef366db8
- https://github.com/acw/simple_asn1
- https://rustsec.org/advisories/RUSTSEC-2021-0125.html
