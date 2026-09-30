# [?] fix(deps): bump anyhow to 1.0.103 to resolve RUSTSEC-2026-0190 (#4882)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-01
Source: https://github.com/matter-labs/zksync-era/commit/8a7adb26ed2adcd3fca21d96ca4130291785d98e
Type: security-commit

## Details
fix(deps): bump anyhow to 1.0.103 to resolve RUSTSEC-2026-0190 (#4882)

## What ❔

Bumps `anyhow` `1.0.98 → 1.0.103` in the `core` workspace lockfile.

## Why ❔

[RUSTSEC-2026-0190](https://rustsec.org/advisories/RUSTSEC-2026-0190)
flags an unsoundness in `anyhow` 1.0.98 (`Error::downcast_mut` after
`Error::context` violates borrow rules, causing UB). The `cargo-deny` CI
runs with `--allow unmaintained`, so this `unsound` advisory fails the
check on every open PR (e.g. #4879). Bumping to the patched `1.0.103`
resolves it without adding a fragile ignore entry to `core/deny.toml`.

Verified locally with `cargo-deny 0.19.9`: `advisories ok, bans ok,
licenses ok, sources ok`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### core/Cargo.lock
```diff
@@ -1015,9 +1015,9 @@ dependencies = [
 
 [[package]]
 name = "anyhow"
-version = "1.0.98"
+version = "1.0.103"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "e16d2d3311acee920a9eb8d33b8cbc1787ce4a264e85f964c2404b969bdcd487"
+checksum = "2a4385e2e34eb35d6b3efe798b9eb88096925d87726c0798709bf56d9ed84af3"
 
 [[package]]
 name = "arbitrary"
```

### core/lib/merkle_tree/src/hasher/proofs.rs
```diff
@@ -59,9 +59,7 @@ impl BlockOutputWithProofs {
             let prev_hash = hasher.fold_merkle_path(&op.merkle_path, prev_entry);
             ensure!(
                 prev_hash == root_hash,
-                "Condition failed: `prev_hash == root_hash` ({:?} vs {:?})",
-                prev_hash,
-                root_hash
+                "Condition failed: `prev_hash == root_hash` ({prev_hash:?} vs {root_hash:?})"
             );
             if let TreeInstruction::Write(new_entry) = instruction {
                 let next_hash = hasher.fold_merkle_path(&op.merkle_path, new_entry);
```

### core/lib/state/src/storage_factory/mod.rs
```diff
@@ -104,9 +104,7 @@ impl CommonStorage<'static> {
         let rocksdb_l1_batch_number = rocksdb.next_l1_batch_number().await;
         if l1_batch_number + 1 != rocksdb_l1_batch_number {
             let err = anyhow::anyhow!(
-                "RocksDB synchronized to L1 batch #{} while #{} was expected",
-                rocksdb_l1_batch_number,
-                l1_batch_number
+                "RocksDB synchronized to L1 batch #{rocksdb_l1_batch_number} while #{l1_batch_number} was expected"
             );
             return Err(err.into());
         }
```
