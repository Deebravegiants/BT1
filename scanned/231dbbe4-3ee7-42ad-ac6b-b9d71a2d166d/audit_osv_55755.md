# [M] Debug output exposes NIP-46 and NIP-60 credentials

## Summary
Severity: Medium
Advisory: RUSTSEC-2026-0225
Ecosystem: crates.io
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0225
Type: osv

## Affected
- crates.io: `nostr` — affected >=0.0.0-0 <0.44.7

## Details
Several NIP-46 and NIP-60 types used derived `Debug` implementations even though
their fields contained credentials or decrypted application data. Formatting these
values exposed NIP-46 connection secrets and request parameters, as well as NIP-60
private keys, Cashu bearer proofs, and quote capability identifiers.

Applications commonly include `Debug` output in diagnostic logs, tracing spans, or
error reports. Anyone able to read those outputs could recover the disclosed
credentials and, depending on the value, impersonate a signer connection or spend
wallet tokens. The issue does not expose data unless an affected value is formatted
and the resulting output is made accessible.

The affected types now use custom `Debug` implementations that preserve variant and
non-sensitive structural information while replacing credentials, bearer values,
and plaintext fields with redaction markers. Serialization and protocol behavior are
unchanged.

## References
- https://crates.io/crates/nostr
- https://rustsec.org/advisories/RUSTSEC-2026-0225.html
- https://github.com/nostrdevkit/nostr/commit/2bc5fa2c270bb87b397d381909053f12ee734d44
- https://github.com/nostrdevkit/nostr/commit/778af7e4930449dcdd7a070774da7b71b282d171
