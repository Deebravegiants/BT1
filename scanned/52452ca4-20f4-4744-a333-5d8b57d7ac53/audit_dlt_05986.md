# [?] Update rand to 0.9.3 to fix RUSTSEC-2026-0097

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/2b433d0109344fecdd7b798ae14ae8e0e406f525
Type: security-commit

## Details
Update rand to 0.9.3 to fix RUSTSEC-2026-0097

rand 0.9.0 is affected by an unsoundness in ThreadRng where a custom
log::Log implementation that calls rand::thread_rng() and triggers a
reseed from inside its log method creates an aliased mutable reference.
Patched in rand 0.9.3 (and rand 0.10.1 on the 0.10.x line).

Bump the workspace rand dep from "0.9" to "0.9.3" so the lockfile
resolves to the patched version, and refresh the main Cargo.lock plus
the two tool lockfiles.

Also drop the rand_07 dep from cfx-rpc-cfx-types: the only consumer was
a Subscribers<T>::rand field holding a rand_07::OsRng to feed into
H64::random_using. Replaced with a new SubId::next() constructor that
uses rand 0.9's rand::random::<[u8; 8]>() and wraps the bytes directly.
This removes a first-party rand 0.7 entry point; the remaining 0.7.3
and 0.8.5 entries in Cargo.lock are forced by external transitive deps
(fixed-hash/jsonrpc-pubsub/parity-* for 0.7.x; ark-std/alloy-rpc-types/
proptest/revm/substrate-bn for 0.8.x) and cannot be removed without
upstream work. Migrating pos/diem-crypto and replacing parity-secp256k1
will be handled in follow-up PRs.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
