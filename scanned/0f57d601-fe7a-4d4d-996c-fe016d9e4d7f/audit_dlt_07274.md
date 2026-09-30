# [?] Add `memory-tracker` feature to `sp-trie` to fix wasm panic (#6745)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-07-30
Source: https://github.com/paritytech/substrate/commit/a5d6c905b663f88d8d7ac2ac5616a4ba4ffcf450
Type: security-commit

## Details
Add `memory-tracker` feature to `sp-trie` to fix wasm panic (#6745)

* Add memory tracker feature to sp-trie to fix wasm panic

* Apply suggestions from code review

Co-authored-by: Bastian Köcher <bkchr@users.noreply.github.com>

Co-authored-by: Bastian Köcher <bkchr@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -3294,9 +3294,9 @@ dependencies = [
 
 [[package]]
 name = "memory-db"
-version = "0.24.0"
+version = "0.24.1"
 source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "0777fbb396f666701d939e9b3876c18ada6b3581257d88631f2590bc366d8ebe"
+checksum = "36f36ddb0b2cdc25d38babba472108798e3477f02be5165f038c5e393e50c57a"
 dependencies = [
  "hash-db",
  "hashbrown 0.8.0",
@@ -3640,6 +3640,7 @@ dependencies = [
  "sp-runtime",
  "sp-timestamp",
  "sp-transaction-pool",
+ "sp-trie",
  "structopt",
  "substrate-browser-utils",
  "substrate-build-script-utils",
@@ -9345,7 +9346,7 @@ version = "1.5.0"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3bfd5b7557925ce778ff9b9ef90e3ade34c524b5ff10e239c69a42d546d2af56"
 dependencies = [
- "rand 0.7.3",
+ "rand 0.3.23",
 ]
 
 [[package]]
```

### bin/node/cli/Cargo.toml
```diff
@@ -109,6 +109,7 @@ browser-utils = { package = "substrate-browser-utils", path = "../../../utils/br
 node-executor = { version = "2.0.0-rc5", path = "../executor", features = [ "wasmtime" ] }
 sc-cli = { version = "0.8.0-rc5", optional = true, path = "../../../client/cli", features = [ "wasmtime" ] }
 sc-service = { version = "0.8.0-rc5", default-features = false, path = "../../../client/service", features = [ "wasmtime" ] }
+sp-trie = { version = "2.0.0-rc5", default-features = false, path = "../../../primitives/trie", features = ["memory-tracker"] }
 
 [dev-dependencies]
 sc-keystore = { version = "2.0.0-rc5", path = "../../../client/keystore" }
```

### primitives/trie/Cargo.toml
```diff
@@ -43,3 +43,4 @@ std = [
 	"trie-root/std",
 	"sp-core/std",
 ]
+memory-tracker = []
```

### primitives/trie/src/lib.rs
```diff
@@ -78,6 +78,11 @@ impl<H: Hasher> TrieConfiguration for Layout<H> {
 	}
 }
 
+#[cfg(not(feature = "memory-tracker"))]
+type MemTracker = memory_db::NoopTracker<trie_db::DBValue>;
+#[cfg(feature = "memory-tracker")]
+type MemTracker = memory_db::MemCounter<trie_db::DBValue>;
+
 /// TrieDB error over `TrieConfiguration` trait.
 pub type TrieError<L> = trie_db::TrieError<TrieHash<L>, CError<L>>;
 /// Reexport from `hash_db`, with genericity set for `Hasher` trait.
@@ -88,13 +93,19 @@ pub type HashDB<'a, H> = dyn hash_db::HashDB<H, trie_db::DBValue> + 'a;
 /// Reexport from `hash_db`, with genericity set for `Hasher` trait.
 /// This uses a `KeyFunction` for prefixing keys internally (avoiding
 /// key conflict for non random keys).
-pub type PrefixedMemoryDB<H> = memory_db::MemoryDB<H, memory_db::PrefixedKey<H>, trie_db::DBValue>;
+pub type PrefixedMemoryDB<H> = memory_db::MemoryDB<
+	H, memory_db::PrefixedKey<H>, trie_db::DBValue, MemTracker
+>;
 /// Reexport from `hash_db`, with genericity set for `Hasher` trait.
 /// This uses a noops `KeyFunction` (key addressing must be hashed or using
 /// an encoding scheme that avoid key conflict).
-pub type MemoryDB<H> = memory_db::MemoryDB<H, memory_db::HashKey<H>, trie_db::DBValue>;
+pub type MemoryDB<H> = memory_db::MemoryDB<
+	H, memory_db::HashKey<H>, trie_db::DBValue, MemTracker,
+>;
 /// Reexport from `hash_db`, with genericity set for `Hasher` trait.
-pub type GenericMemoryDB<H, KF> = memory_db::MemoryDB<H, KF, trie_db::DBValue>;
+pub type GenericMemoryDB<H, KF> = memory_db::MemoryDB<
+	H, KF, trie_db::DBValue, MemTracker
+>;
 
 /// Persistent trie database read-access interface for the a given hasher.
 pub type TrieDB<'a, L> = trie_db::TrieDB<'a, L>;
```
