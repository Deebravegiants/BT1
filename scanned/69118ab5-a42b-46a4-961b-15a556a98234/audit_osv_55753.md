# [H] Remote Denial of Service via malformed NIP‑44 v2 payload

## Summary
Severity: High
Advisory: RUSTSEC-2026-0216
Aliases: GHSA-hrqp-8w79-gwgw
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0216
Type: osv

## Affected
- crates.io: `nostr` — affected >=0.45.0-alpha.1 <0.45.0-alpha.5

## Details
The NIP-44 v2 decryption path in the `nostr` crate contains a reachable panic
when processing a short or empty ciphertext. After the HMAC check passes and the
ciphertext is decrypted via ChaCha20, the code reads a 2‑byte unpadded‑length
prefix via `buffer[0..2]` without first verifying that the decrypted buffer
contains at least 2 bytes. A malicious sender who holds the symmetric
conversation key (e.g., a direct‑message sender) can craft a payload that
produces a 0 or 1‑byte decrypted buffer, causing an index‑out‑of‑bounds panic.
This can be triggered remotely through any relay that delivers the crafted
event to the victim's client, resulting in a denial of service. No key material,
plaintext, or memory corruption occurs.

The vulnerability is present in all versions from `0.26.0` up to `0.44.4`
(inclusive) and in the alpha releases `0.45.0‑alpha.1` through `0.45.0‑alpha.4`.
Versions `0.44.5` and `0.45.0‑alpha.5` contain the fix.

## Credit

Discovered and responsibly disclosed by **Muhammed Shekho** ([mhd-shekho.com](https://mhd-shekho.com)).

## References
- https://crates.io/crates/nostr
- https://rustsec.org/advisories/RUSTSEC-2026-0216.html
- https://github.com/nostrdevkit/nostr/commit/73bdd677b872641d57a2ebcc5afc23ee0e5f0d2d
