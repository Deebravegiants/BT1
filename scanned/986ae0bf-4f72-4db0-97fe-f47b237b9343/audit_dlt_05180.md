# [?] Drop stale RUSTSEC-2026-0097 ignore

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-07-02
Source: https://github.com/Conflux-Chain/conflux-rust/commit/90febe83aba0eb8661100b4951d68e1294ecf6f9
Type: security-commit

## Details
Drop stale RUSTSEC-2026-0097 ignore

rand 0.7 is gone from the tree and the remaining rand 0.8.6 contains the backported ThreadRng fix, so the advisory no longer matches any crate (cargo-deny warned advisory-not-detected).

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

## Patch
### deny.toml
```diff
@@ -80,18 +80,6 @@ ignore = [
     "RUSTSEC-2024-0436",
     # instant unmaintained; pulled by parking_lot 0.11 via prometheus 0.12.
     "RUSTSEC-2024-0384",
-    # rand 0.7/0.8 unsound `ThreadRng` reseed-in-custom-logger
-    # (RUSTSEC-2026-0097). The 0.9.x code path is patched here by bumping
-    # workspace rand to 0.9.3. rand 0.7.3 and 0.8.5 still appear in
-    # Cargo.lock via external transitive deps that cannot be upgraded
-    # without upstream work (fixed-hash, parity-secp256k1,
-    # ark-std, alloy-rpc-types, proptest, revm,
-    # substrate-bn for 0.8.x) and first-party pos/diem-crypto plus cfx_key
-    # bound to the unmaintained parity-secp256k1 fork. The exploit requires
-    # a custom log::Log impl that calls rand::thread_rng() inside its log
-    # method and triggers a reseed there, which this repo does not do.
-    # Follow-ups will migrate pos/diem-crypto and replace parity-secp256k1.
-    { id = "RUSTSEC-2026-0097", reason = "rand 0.9 patched; 0.7/0.8 forced by transitive deps and upstream pins; vulnerable code path not reachable here." },
     # proc-macro-error2 is unmaintained; pulled by alloy-sol-macro 1.6.0
     "RUSTSEC-2026-0173",
     # quick-xml DoS advisories (quadratic duplicate-attribute check;
```
