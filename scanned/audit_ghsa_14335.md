# [M] h2 vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-f8vr-r385-rh5r
CVE: CVE-2023-26964
CWE: CWE-770
Ecosystem: crates.io
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-f8vr-r385-rh5r
Type: github-advisory

## Affected
- crates.io: `h2` — affected >=0 <0.3.17

## Details
Hyper is an HTTP library for Rust and h2 is an HTTP 2.0 client & server implementation for Rust. An issue was discovered in h2 v0.2.4 when processing header frames. It incorrectly processes the HTTP2 `RST_STREAM` frames by not always releasing the memory immediately upon receiving the reset frame, leading to stream stacking. As a result, the memory and CPU usage are high which can lead to a Denial of Service (DoS).

This issue affects users only when dealing with http2 connections.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26964
- https://github.com/hyperium/h2/issues/621
- https://github.com/hyperium/hyper/issues/2877
- https://github.com/hyperium/h2/pull/668
- https://github.com/hyperium/hyper
- https://rustsec.org/advisories/RUSTSEC-2023-0034.html
