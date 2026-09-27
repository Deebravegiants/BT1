# [H] Verification cache poisoning allows forged Nostr events to bypass signature validation

## Summary
Severity: High
Advisory: RUSTSEC-2026-0224
Aliases: GHSA-f96q-5f6p-v7cj
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0224
Type: osv

## Affected
- crates.io: `nostr-relay-pool` — affected >=0.0.0-0 <0.44.2

## Details
The `nostr-relay-pool` crate cached the result of event signature verification
before the check was actually performed. Because the entry was inserted
unconditionally, a first delivery whose signature failed was still recorded
in the cache. A subsequent delivery of the same event (identical ID,
but with a forged signature) would then hit the cache, causing signature
verification to be skipped entirely. The forged event was passed on to
`NostrDatabase::save_event()` as if it had been validated.

Applications that connect to untrusted or compromised Nostr relays and persist
received events are vulnerable. An attacker can inject arbitrary events
without a valid signature into the application's trusted database, enabling
impersonation of any public key or corruption of application state derived from
stored events.

The issue does not compromise confidentiality or availability. It solely
undermines the integrity of stored event data.

The fix, released in version 0.44.2, moves the cache insertion to occur only
after a successful signature verification, so that failed attempts never create
a cache entry.

## Credit

Discovered and reported by [Ali Al-Sorehi](https://github.com/aykoooo)

## References
- https://crates.io/crates/nostr-relay-pool
- https://rustsec.org/advisories/RUSTSEC-2026-0224.html
- https://github.com/nostrdevkit/nostr/commit/02a88bd5688de058bfba8aa9fb4612441a384eff
