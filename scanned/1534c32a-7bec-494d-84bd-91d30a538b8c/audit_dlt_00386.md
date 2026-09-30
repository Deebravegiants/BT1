# [?] Bump crossbeam-epoch to 0.9.20 to fix RUSTSEC-2026-0204 (#27167)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-07-07
Source: https://github.com/MystenLabs/sui/commit/a17b4691909890b915fcdea8b2442da5f4b3bd6e
Type: security-commit

## Details
Bump crossbeam-epoch to 0.9.20 to fix RUSTSEC-2026-0204 (#27167)

## Description

The `cargo-deny (advisories)` CI job is failing on main due to
[RUSTSEC-2026-0204](https://rustsec.org/advisories/RUSTSEC-2026-0204)
(invalid pointer dereference in `fmt::Pointer` impl for
`Atomic`/`Shared` in crossbeam-epoch < 0.9.20). Bump the locked version
to 0.9.20 in the root, `external-crates/move`, and `examples/rust/*`
lockfiles.

## Test plan

`cargo deny check advisories` passes locally for both the root workspace
and `external-crates/move` with this change (it was the only outstanding
advisory).

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol:
- [ ] Nodes (Validators and Full nodes):
- [ ] gRPC:
- [ ] JSON-RPC:
- [ ] GraphQL:
- [ ] CLI:
- [ ] Rust SDK:

## Patch
### Cargo.lock
```diff
@@ -4093,9 +4093,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```

### examples/rust/basic-sui-indexer/Cargo.lock
```diff
@@ -1732,9 +1732,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```

### examples/rust/clickhouse-sui-indexer/Cargo.lock
```diff
@@ -1824,9 +1824,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```

### examples/rust/walrus-attributes-indexer/Cargo.lock
```diff
@@ -1716,9 +1716,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```

### external-crates/move/Cargo.lock
```diff
@@ -822,9 +822,9 @@ dependencies = [
 
 [[package]]
 name = "crossbeam-epoch"
-version = "0.9.18"
+version = "0.9.20"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "5b82ac4a3c2ca9c3460964f020e1402edd5753411d7737aa39c3714ad1b5420e"
+checksum = "2d6914041f254d6e9176c01941b21115dcfb7089e55135a35411081bd106ef3f"
 dependencies = [
  "crossbeam-utils",
 ]
```
