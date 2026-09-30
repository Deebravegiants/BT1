# [?] fix(kona/mpt): guard against panic when prefix longer than path in Extension node (#19728)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-06-16
Source: https://github.com/ethereum-optimism/optimism/commit/40d8cf29c2c27c25bbd7e86e91cc40e7412a9310
Type: security-commit

## Details
fix(kona/mpt): guard against panic when prefix longer than path in Extension node (#19728)

Adds a length check before slicing in `TrieNode::open` to prevent a
panic when `prefix.len()` exceeds `path.len()` for Extension nodes.

Adds a unit test that calls `TrieNode::open` on an Extension node with
a path shorter than the prefix, verifying it returns `Ok(None)` rather
than panicking. Also enables the `thread_rng` feature for `rand` in
dev-dependencies so the existing proptest compiles.

Co-authored-by: Einar Rasmussen <einar@oplabs.com>
Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

## Patch
### rust/kona/crates/proof/mpt/Cargo.toml
```diff
@@ -32,7 +32,7 @@ alloy-transport-http.workspace = true
 alloy-rpc-types = { workspace = true, features = ["eth", "debug"] }
 
 # General
-rand.workspace = true
+rand = { workspace = true, features = ["thread_rng"] }
 reqwest.workspace = true
 proptest.workspace = true
 tokio = { workspace = true, features = ["full"] }
```

### rust/kona/crates/proof/mpt/src/node.rs
```diff
@@ -162,7 +162,12 @@ impl TrieNode {
                     .unwrap_or(Ok(None))
             }
             Self::Leaf { prefix, value } => Ok((path == prefix).then_some(value)),
-            Self::Extension { prefix, node } => {
+            Self::Extension { prefix, node: _ } if path.len() < prefix.len() => {
+                Err(TrieNodeError::PathTooShort)
+            }
+            Self::Extension { prefix, node } =>
+            // Implied `path.len() >= prefix.len()`
+            {
                 if path.slice(..prefix.len()) == *prefix {
                     // Follow extension branch
                     node.unblind(fetcher)?;
@@ -794,6 +799,25 @@ mod test {
         assert_eq!(node, expected);
     }
 
+    #[test]
+    fn test_extension_open_path_shorter_than_prefix_no_panic() {
+        // Regression test: `open` must not panic when the path is shorter than the
+        // extension prefix. Previously, `path.slice(..prefix.len())` would panic in
+        // this case; now it returns `Err(PathTooShort)`, consistent with how a branch
+        // node reports an exhausted path.
+        let leaf = TrieNode::Leaf { prefix: Nibbles::default(), value: bytes!("deadbeef") };
+        let mut node = TrieNode::Extension {
+            prefix: Nibbles::from_nibbles([0x0a, 0x0b, 0x0c]),
+            node: Box::new(leaf),
+        };
+        // Path has only 1 nibble; prefix has 3 — previously would panic.
+        let short_path = Nibbles::from_nibbles([0x0a]);
+        assert!(matches!(
+            node.open(&short_path, &NoopTrieProvider),
+            Err(TrieNodeError::PathTooShort)
+        ));
+    }
+
     proptest::proptest! {
         /// Differential test for inserting an arbitrary number of keys into an empty `TrieNode` / `HashBuilder`.
         #[test]
```
