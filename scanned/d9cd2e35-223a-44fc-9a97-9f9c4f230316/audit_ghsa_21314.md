# [M] matrix-sdk 0.6.0 logs access tokens

## Summary
Severity: Medium
Advisory: GHSA-fc4h-xcf3-qj5f
Ecosystem: crates.io
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-fc4h-xcf3-qj5f
Type: github-advisory

## Affected
- crates.io: `matrix-sdk` — affected >=0.6.0 <0.6.2

## Details
When sending Matrix requests using an affected version of `matrix-sdk` in an application that writes logs using `tracing-subscriber` (in a way that includes fields of tracing spans such as `tracing_subscriber`s default text output from the `fmt` module), these logs will contain the user's access token.

## References
- https://github.com/matrix-org/matrix-rust-sdk/issues/1110
- https://github.com/matrix-org/matrix-rust-sdk
- https://rustsec.org/advisories/RUSTSEC-2022-0062.html
