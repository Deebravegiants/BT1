# [H] Wallet event parsers accept unauthenticated events

## Summary
Severity: High
Advisory: RUSTSEC-2026-0226
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0226
Type: osv

## Affected
- crates.io: `nostr` — affected >=0.0.0-0 <0.44.7

## Details
The NIP-47 response and notification parsers and the NIP-60 wallet event parsers
decrypted relay-provided events before verifying their kind, computed event ID,
signature, and expected wallet public key. The decryption peer was derived from the
untrusted event author, so successful decryption did not prove that the configured
wallet created the event.

An attacker can sign an event with their own key and derive the corresponding shared
secret with the victim's public key. A malicious relay delivering that event could
therefore cause attacker-chosen encrypted content to be parsed as a response,
notification, token, spending record, or quote from the configured wallet. This can
corrupt wallet state or cause an application to act on forged wallet data. The issue
does not expose the victim's private key or decrypt events authored by the legitimate
wallet.

The affected parsers now verify the event kind, ID, signature, and exact configured
wallet author before attempting decryption or parsing the plaintext.

## References
- https://crates.io/crates/nostr
- https://rustsec.org/advisories/RUSTSEC-2026-0226.html
- https://github.com/nostrdevkit/nostr/commit/2b6d6227cd884c1acb200bffa66a3f402b02a176
- https://github.com/nostrdevkit/nostr/commit/0b78464e39604b0f052862035f47fdabc2a536dd
