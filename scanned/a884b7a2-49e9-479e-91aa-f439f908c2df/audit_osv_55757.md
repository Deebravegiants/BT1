# [H] NIP-44 v2 decryption permits resource exhaustion

## Summary
Severity: High
Advisory: RUSTSEC-2026-0227
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0227
Type: osv

## Affected
- crates.io: `nostr` — affected >=0.0.0-0 <0.44.7

## Details
The NIP-44 decryption entry point Base64-decoded the complete attacker-controlled
payload before determining its version or enforcing any size limit. For v2 payloads,
the decoded buffer was then authenticated with HMAC even when it was much larger than
the maximum payload supported by the crate's current v2 codec.

A malicious relay or event author could deliver an oversized value to an application
that decrypts NIP-44 content. The value caused memory allocation and Base64 and HMAC
work proportional to its size before authentication failed; knowledge of the
conversation key was not required to consume those initial resources. Repeated
payloads could exhaust memory or CPU and make the receiving application unavailable.
The issue does not disclose plaintext or key material and does not bypass message
authentication.

Decryption now reads only the encoded version prefix first, derives the bound from
the largest payload the current v2 encoder can emit, and rejects oversized encoded
and decoded payloads before full allocation or HMAC processing. The limit remains in
the v2 implementation so a future codec with a different length format can define its
own bound.

## References
- https://crates.io/crates/nostr
- https://rustsec.org/advisories/RUSTSEC-2026-0227.html
- https://github.com/nostrdevkit/nostr/commit/89dc1a77eaa774174588c5a38b6324c502948830
