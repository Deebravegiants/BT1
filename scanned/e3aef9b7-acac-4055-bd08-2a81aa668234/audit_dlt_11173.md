# [?] fix: partial smt with root and empty leaves panics during deserialization (#662)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-11-23
Source: https://github.com/0xMiden/miden-vm/commit/05e66c62d3e5417a0834137003317c7cc8cca1ce
Type: security-commit

## Details
fix: partial smt with root and empty leaves panics during deserialization (#662)

## Patch
### CHANGELOG.md
```diff
@@ -1,4 +1,8 @@
-## 1.18.3 (2025-11-22)
+## 0.18.4 (TODO)
+
+- Fixed serialization of `PartialSmt` panicking in debug mode when it was constructed from only a root ([#662](https://github.com/0xMiden/crypto/pull/662)).
+
+## 0.18.3 (2025-11-22)
 
 - [BREAKING] removed unused 'self' parameter in HasherExt and all its implementations ([#666](https://github.com/0xMiden/crypto/pull/666))
 
```

### miden-crypto/src/merkle/smt/partial.rs
```diff
@@ -386,7 +386,20 @@ impl Deserializable for PartialSmt {
             nodes.insert(idx, node);
         }
 
-        let smt = Smt::from_raw_parts(nodes, leaves, root);
+        // If the leaves are empty, the set root may not match the root of the inner nodes, which
+        // causes from_raw_parts to panic. In this case, we bypass this check by constructing the
+        // SMT with the expected root and overwriting it afterward.
+        let smt = if leaves.is_empty() {
+            let inner_node_root =
+                nodes.get(&NodeIndex::root()).map(InnerNode::hash).unwrap_or(Smt::EMPTY_ROOT);
+            let mut smt = Smt::from_raw_parts(nodes, leaves, inner_node_root);
+            smt.set_root(root);
+            smt
+        } else {
+            // If the leaves are not empty, the root should match.
+            Smt::from_raw_parts(nodes, leaves, root)
+        };
+
         Ok(PartialSmt(smt))
     }
 }
@@ -739,6 +752,13 @@ mod tests {
         assert!(!PartialSmt::default().tracks_leaves());
     }
 
+    /// `PartialSmt` serde round-trip when constructed from just a root.
+    #[test]
+    fn partial_smt_with_empty_leaves_serialization_roundtrip() {
+        let partial_smt = PartialSmt::new(rand_value());
+        assert_eq!(partial_smt, PartialSmt::read_from_bytes(&partial_smt.to_bytes()).unwrap());
+    }
+
     /// `PartialSmt` serde round-trip. Also tests conversion from SMT.
     #[test]
     fn partial_smt_serialization_roundtrip() {
```
