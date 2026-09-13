# [?] fix: preserve leading zero bytes and handle all-0xFF overflow in rich-indexer prefix search upper bound (#5166)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-04-10
Source: https://github.com/nervosnetwork/ckb/commit/5ebbc3921f392184a8f4c7dfb743159c65281c1a
Type: security-commit

## Details
fix: preserve leading zero bytes and handle all-0xFF overflow in rich-indexer prefix search upper bound (#5166)

### What problem does this PR solve?

Issue Number: close #5165

Problem Summary:

`get_binary_upper_boundary()` uses `BigUint::to_bytes_be()` which strips
leading zero bytes. For a 22-byte input like `00 01 4c bc ... 86 6e`,
the computed upper bound becomes `01 4c bc ... 86 6f` (21 bytes). Since
bytea comparison is lexicographic, the shorter result is far larger than
intended, causing prefix queries (`args >= $prefix AND args < $upper`)
to massively over-match — e.g. returning 103k scripts instead of 2.

~2.4% of mainnet scripts are affected (args starting with `0x00`),
spanning ACP locks, JoyID, CoTA, and others.

Additionally, when the input is all `0xFF` bytes, incrementing via
`BigUint` produces `[0x01, 0x00, ...]` which is lexicographically
*smaller* than `[0xFF, ...]` in bytea comparison (because `0x01 < 0xFF`
at byte 0), causing the prefix query to match **nothing**.

### What is changed and how it works?

What's Changed:

- Replaced `BigUint` with a direct lexicographic successor computation
on the byte slice using `rposition`: find the rightmost byte that is not
`u8::MAX`, increment it, then truncate everything after it. This
produces the shortest byte string that is strictly greater than every
possible extension of the input prefix, which is exactly what the range
query needs:

```rust
if let Some(i) = value.iter().rposition(|&b| b != u8::MAX) {
    let mut result = value[..=i].to_vec();
    result[i] += 1;
    result
} else {
    // All bytes are u8::MAX — return a sentinel one byte longer
    vec![u8::MAX; value.len() + 1]
}
```

- For the all-`0xFF` overflow case, returns `vec![u8::MAX; value.len() +
1]` — a sentinel that is lexicographically greater than any extension of
the input in bytea comparison.

- Removed the now-unused `num-bigint` dependency from both
`ckb-rich-indexer` (`util/rich-indexer/Cargo.toml`) and the workspace
root (`./Cargo.toml`).

- Uses `u8::MAX` instead of `0xFF` literals throughout for clarity.

- Added 8 regression tests: real-world 22-byte args from the report,
multiple leading zeros, single zero byte, all-`0xFF` overflow sentinel,
carry propagation with truncation (e.g. `[0x00, u8::MAX, u8::MAX]` →
`[0x01]`), short prefix `0x003d`, and standard increment cases.

### Related changes

- Need to cherry-pick to the release branch

### Check List

Tests

- Unit test

Side effects

- None

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: quake <8990+quake@users.noreply.github.com>
Co-authored-by: eval-exec <46400566+eval-exec@users.noreply.github.com>

### Cargo.lock
```diff
@@ -1574,7 +1574,6 @@ dependencies = [
  "hex",
  "include_dir",
  "log",
- "num-bigint",
  "rand 0.8.5",
  "serde_json",
  "sql-builder",
@@ -4397,16 +4396,6 @@ dependencies = [
  "winapi",
 ]
 
-[[package]]
-name = "num-bigint"
-version = "0.4.6"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a5e44f723f1133c9deac646763579fdb3ac745e418f2a7af9cd0c431da1f20b9"
-dependencies = [
- "num-integer",
- "num-traits",
-]
-
 [[package]]
 name = "num-bigint-dig"
 version = "0.8.4"
```

### Cargo.toml
```diff
@@ -264,7 +264,6 @@ minstant = "0.1.4"
 molecule = { version = "0.9.0", default-features = false }
 multi_index_map = "0.15.0"
 multiaddr = { version = "0.3.6", package = "tentacle-multiaddr" }
-num-bigint = "0.4"
 num_cpus = "1.16.0"
 numext-fixed-uint = "0.1"
 p2p = { version = "0.7.1", package = "tentacle", default-features = false }
```

### util/rich-indexer/Cargo.toml
```diff
@@ -21,7 +21,6 @@ ckb-notify.workspace = true
 ckb-types.workspace = true
 futures.workspace = true
 log.workspace = true
-num-bigint.workspace = true
 sql-builder.workspace = true
 sqlx = { workspace = true, features = ["runtime-tokio-rustls", "any", "sqlite", "postgres"] }
 include_dir.workspace = true
```

### util/rich-indexer/src/indexer_handle/async_indexer_handle/mod.rs
```diff
@@ -12,7 +12,7 @@ use ckb_jsonrpc_types::{
     IndexerTip, JsonBytes,
 };
 use ckb_types::H256;
-use num_bigint::BigUint;
+
 use sql_builder::SqlBuilder;
 use sqlx::Row;
 
@@ -250,11 +250,23 @@ fn build_cell_filter(
 
 fn get_binary_upper_boundary(value: &[u8]) -> Vec<u8> {
     if value.is_empty() {
-        return vec![255; 32];
+        return vec![u8::MAX; 32];
+    }
+    // Compute the lexicographic successor: find the rightmost byte that is
+    // not u8::MAX, increment it, then truncate everything after it. The result
+    // is the shortest byte string that is strictly greater than every possible
+    // extension of `value`, which is exactly what the prefix range query
+    // `args >= $prefix AND args < $upper` needs.
+    if let Some(i) = value.iter().rposition(|&b| b != u8::MAX) {
+        let mut result = value[..=i].to_vec();
+        result[i] += 1;
+        result
+    } else {
+        // All bytes are u8::MAX — no finite exclusive upper bound exists for
+        // this prefix. Return a sentinel one byte longer that is still
+        // lexicographically greater than any extension of the input.
+        vec![u8::MAX; value.len() + 1]
     }
-    let value_big = BigUint::from_bytes_be(value);
-    let value_upper = value_big + 1usize;
-    value_upper.to_bytes_be()
 }
 
 fn bytes_to_h256(input: &[u8]) -> H256 {
@@ -367,4 +379,63 @@ mod tests {
         let result = get_binary_upper_boundary(&input);
         assert_eq!(result, expected);
     }
+
+    // Regression test for https://github.com/nervosnetwork/ckb/issues/5165
+    // Verifies that leading zero bytes are preserved in the upper boundary.
+    #[test]
+    fn test_get_binary_upper_boundary_leading_zeros() {
+        // Real-world case from the bug report: 22-byte args starting with 0x00
+        let input =
+            hex::decode("00014cbca1cb3cd2b60550904f16c920cffa7c9f866e").expect("Decoding failed");
+        let expected =
+            hex::decode("00014cbca1cb3cd2b60550904f16c920cffa7c9f866f").expect("Decoding failed");
+        let result = get_binary_upper_boundary(&input);
+        assert_eq!(
+            result.len(),
+            input.len(),
+            "Upper boundary must preserve the original byte length"
+        );
+        assert_eq!(result, expected);
+    }
+
+    #[test]
+    fn test_get_binary_upper_boundary_multiple_leading_zeros() {
+        let input = hex::decode("0000000102").expect("Decoding failed");
+        let expected = hex::decode("0000000103").expect("Decoding failed");
+        let result = get_binary_upper_boundary(&input);
+        assert_eq!(result.len(), input.len());
+        assert_eq!(result, expected);
+    }
+
+    #[test]
+    fn test_get_binary_upper_boundary_single_zero_byte() {
+        let result = get_binary_upper_boundary(&[0x00]);
+        assert_eq!(result, vec![0x01]);
+    }
+
+    #[test]
+    fn test_get_binary_upper_boundary_all_ff_overflow() {
+        // When all bytes are u8::MAX, no same-length upper bound exists.
+        // The function returns a sentinel of u8::MAX bytes one byte longer.
+        let result = get_binary_upper_boundary(&[u8::MAX, u8::MAX]);
+        assert_eq!(result, vec![u8::MAX; 3]);
+    }
+
+    #[test]
+    fn test_get_binary_upper_boundary_trailing_ff_carry() {
+        // Trailing u8::MAX bytes are truncated; only the incremented byte remains
+        let input = vec![0x00, u8::MAX, u8::MAX];
+        let result = get_binary_upper_boundary(&input);
+        assert_eq!(result, vec![0x01]);
+    }
+
+    #[test]
+    fn test_get_binary_upper_boundary_short_prefix_with_leading_zero() {
+        // Short prefix search case from the bug report: args "0x003d"
+        let input = hex::decode("003d").expect("Decoding failed");
+        let expected = hex::decode("003e").expect("Decoding failed");
+        let result = get_binary_upper_boundary(&input);
+        assert_eq!(result.len(), input.len());
+        assert_eq!(result, expected);
+    }
 }
```
