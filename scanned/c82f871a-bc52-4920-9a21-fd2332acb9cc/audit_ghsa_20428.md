# [H] Race Condition in tokio

## Summary
Severity: High
Advisory: GHSA-fg7r-2g4j-5cgr
CVE: CVE-2021-45710
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-fg7r-2g4j-5cgr
Type: github-advisory

## Affected
- crates.io: `tokio` — affected >=0.1.14 <1.8.4
- crates.io: `tokio` — affected >=1.9.0 <1.13.1

## Details
If a tokio::sync::oneshot channel is closed (via the oneshot::Receiver::close method), a data race may occur if the oneshot::Sender::send method is called while the corresponding oneshot::Receiver is awaited or calling try_recv.

When these methods are called concurrently on a closed channel, the two halves of the channel can concurrently access a shared memory location, resulting in a data race. This has been observed to cause memory corruption.

Note that the race only occurs when both halves of the channel are used after the Receiver half has called close. Code where close is not used, or where the Receiver is not awaited and try_recv is not called after calling close, is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45710
- https://github.com/tokio-rs/tokio/issues/4225
- https://github.com/tokio-rs/tokio
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tokio/RUSTSEC-2021-0124.md
- https://rustsec.org/advisories/RUSTSEC-2021-0124.html
