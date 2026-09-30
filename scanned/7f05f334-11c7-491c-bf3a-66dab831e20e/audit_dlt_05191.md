# [?] deny.toml: ignore RUSTSEC-2026-0097 for rand 0.7/0.8

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-04-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f0e7e217dc658031347da9e1ee4910051a3f1778
Type: security-commit

## Details
deny.toml: ignore RUSTSEC-2026-0097 for rand 0.7/0.8

The main fix (rand 0.9 → 0.9.3) is applied in the previous commit, but
rand 0.7.3 and 0.8.5 still appear in Cargo.lock via external transitive
deps and first-party code pinned to upstream crates that haven't been
migrated yet (see commit message above and the deny.toml comment). The
newer cargo-deny used by CI detects the advisory on those versions and
fails the job. Add an ignore with the detailed reason so CI passes while
follow-up work removes the remaining first-party pins.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### deny.toml
```diff
@@ -82,6 +82,18 @@ ignore = [
     "RUSTSEC-2020-0016",
     # instant unmaintained; pulled by parking_lot 0.11 via jsonrpc + prometheus 0.12.
     "RUSTSEC-2024-0384",
+    # rand 0.7/0.8 unsound `ThreadRng` reseed-in-custom-logger
+    # (RUSTSEC-2026-0097). The 0.9.x code path is patched here by bumping
+    # workspace rand to 0.9.3. rand 0.7.3 and 0.8.5 still appear in
+    # Cargo.lock via external transitive deps that cannot be upgraded
+    # without upstream work (fixed-hash, jsonrpc-pubsub, parity-secp256k1,
+    # parity-ws for 0.7.x; ark-std, alloy-rpc-types, proptest, revm,
+    # substrate-bn for 0.8.x) and first-party pos/diem-crypto plus cfx_key
+    # bound to the unmaintained parity-secp256k1 fork. The exploit requires
+    # a custom log::Log impl that calls rand::thread_rng() inside its log
+    # method and triggers a reseed there, which this repo does not do.
+    # Follow-ups will migrate pos/diem-crypto and replace parity-secp256k1.
+    { id = "RUSTSEC-2026-0097", reason = "rand 0.9 patched; 0.7/0.8 forced by transitive deps and upstream pins; vulnerable code path not reachable here." },
 ]
 # If this is true, then cargo deny will use the git executable to fetch advisory database.
 # If this is false, then it uses a built-in git library.
```
