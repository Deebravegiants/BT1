# [H] Quinn: Remote memory exhaustion in quinn-proto from unbounded out-of-order stream reassembly

## Summary
Severity: High
Advisory: GHSA-4w2j-m93h-cj5j
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-4w2j-m93h-cj5j
Type: github-advisory

## Affected
- crates.io: `quinn-proto` — affected >=0.1.0 <0.11.15

## Details
## Summary

The `Assembler` component that assembles unordered stream fragments into consecutive chunks of the stream incurs some overhead for non-contiguous fragments. Readers that read from a `RecvStream` in order (through an `AsyncRead` impl for example) will be sensitive to peers that send fragments while leaving out early parts of the stream, and in particular, fragments with many gaps (because these cannot be defragmented). In such a scenario, the receiving connection suffers from high buffer overhead, enabling memory exhaustion.

## References
- https://github.com/quinn-rs/quinn/security/advisories/GHSA-4w2j-m93h-cj5j
- https://github.com/quinn-rs/quinn/pull/2694
- https://github.com/quinn-rs/quinn/commit/fed0321a9a672819662caab37f5662f1ad91308e
- https://github.com/quinn-rs/quinn
- https://github.com/quinn-rs/quinn/releases/tag/quinn-proto-0.11.15
- https://rustsec.org/advisories/RUSTSEC-2026-0185.html
