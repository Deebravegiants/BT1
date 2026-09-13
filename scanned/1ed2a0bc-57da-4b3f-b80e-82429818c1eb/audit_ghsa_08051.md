# [H] Bug fixes in hpke-rs, hpke-rs-rust-crypto

## Summary
Severity: High
Advisory: GHSA-g433-pq76-6cmf
CWE: CWE-190, CWE-20, CWE-697
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-13
Source: https://github.com/advisories/GHSA-g433-pq76-6cmf
Type: github-advisory

## Affected
- crates.io: `hpke-rs` — affected >=0 <0.6.0
- crates.io: `hpke-rs-rust-crypto` — affected >=0 <0.6.0

## Details
We publish a GitHub security advisory for any releases whose CHANGELOG includes bug-fixes, and encourage our users to upgrade. The latest releases of the hpke-rs and hpke-rs-rust-crypto crates contain the following bug-fixes:

## hpke-rs
- [#127](https://github.com/cryspen/hpke-rs/pull/127): Fix `KemAlgorithm::TryFrom<u16>` mapping where `0x004D` incorrectly resolved to `XWingDraft06` instead of `XWingDraft06Obsolete`.
- [#123](https://github.com/cryspen/hpke-rs/pull/123): Fix potential overflow in context counter and switch to use u64.
- [#128](https://github.com/cryspen/hpke-rs/pull/128): Return errors when trying to use open/seal with export only ciphersuite and when using kdf export with an output that's too long (instead of truncating it)

The issue fixed in #123 was first reported by Nadim Kobeissi.
The issues fixed in #127 and #128 were first reported by Scott Arciszewski.

## hpke-rs-rust-crypto
- [#124](https://github.com/cryspen/hpke-rs/pull/124): Error out on x25519 0 keys

The issue fixed in #124 was first reported by Nadim Kobeissi.

## References
- https://github.com/cryspen/hpke-rs/security/advisories/GHSA-g433-pq76-6cmf
- https://github.com/cryspen/hpke-rs/pull/123
- https://github.com/cryspen/hpke-rs/pull/124
- https://github.com/cryspen/hpke-rs/pull/127
- https://github.com/cryspen/hpke-rs/pull/128
- https://github.com/cryspen/hpke-rs/commit/1c247b5c9aeca602ad2971c9bd49817fe2c308e6
- https://github.com/cryspen/hpke-rs/commit/25248bd624cc0325c98a05c169a0c9aa0aced632
- https://github.com/cryspen/hpke-rs/commit/3a8254938f43bdc4e0c9c4f987f8071f19779066
- https://github.com/cryspen/hpke-rs/commit/b54c8bb83906331bdf4f606cafa30cd7fd20b531
- https://github.com/cryspen/hpke-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0070.html
- https://rustsec.org/advisories/RUSTSEC-2026-0072.html
