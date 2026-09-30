# [?] chore: ignore RUSTSEC-2026-0269 (#6830)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-08-31
Source: https://github.com/chainflip-io/chainflip-backend/commit/aa91d337b4ea723d2ca67bcb025b4d2f575c67b5
Type: security-commit

## Details
chore: ignore RUSTSEC-2026-0269 (#6830)

## Patch
### .cargo/config.toml
```diff
@@ -86,6 +86,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2026-0222: Wasmtime type-index mixup between multiple engines. Low severity embedder-API-misuse issue; we only execute the trusted runtime wasm and don't control the wasmtime version (pinned by polkadot-sdk). Dependency of substrate.
 # - RUSTSEC-2026-0253: Unsoundness in `lru::LruCache::pop()` when the key's `Drop` panics. Our own dependency is on the patched 0.18.2; the remaining 0.12.5 is pinned by libp2p, where `libp2p-identify` doesn't use `lru` at all and `libp2p-swarm`'s only `pop()` is keyed by `Multiaddr`, which has no `Drop` impl.
 # - RUSTSEC-2026-0258: h2 unbounded empty DATA frames. Low severity DoS. Patched where possible, but still some transitive dependencies are unpatched.
+# - RUSTSEC-2026-0269: Wasmtime issue that relies on accessing the file system and the presence of symlinks with trailing slashes.
 
 #
 cf-audit = '''
@@ -139,6 +140,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2026-0222
 	--ignore RUSTSEC-2026-0253
 	--ignore RUSTSEC-2026-0258
+	--ignore RUSTSEC-2026-0269
 '''
 
 [build]
```
