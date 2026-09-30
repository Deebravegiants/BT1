# [?] chore: cargo audit ignore RUSTSEC-2026-0006 (#6412)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2026-02-12
Source: https://github.com/chainflip-io/chainflip-backend/commit/5156ea1b47260fbecaa9249579c097d386536651
Type: security-commit

## Details
chore: cargo audit ignore RUSTSEC-2026-0006 (#6412)

## Patch
### .cargo/config.toml
```diff
@@ -61,6 +61,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2025-0141: Unmaintained bincode crate. Wasmtime dependency.
 # - RUSTSEC-2026-0002: Unsoundness in the lru crate. Our immediate dependency is patched, but not the transitive dependency, which is limited to libp2p-identify and smoldot crates.
 # - RUSTSEC-2026-0009: Medium severity, but only exploitable if user-provided strings are parsed into a time format by the `time` dependency.
+# - RUSTSEC-2026-0006: Impact is unlikely and upgrading requires polkadot-sdk bump.
 cf-audit = '''
 audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2021-0139
@@ -90,6 +91,7 @@ audit -D unmaintained -D unsound
 	--ignore RUSTSEC-2026-0002
 	--ignore RUSTSEC-2026-0007
 	--ignore RUSTSEC-2026-0009
+	--ignore RUSTSEC-2026-0006
 '''
 
 [build]
```
