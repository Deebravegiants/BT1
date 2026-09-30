# [?] fix(merkle): Remove potential overflow in to_scalar_index (#888)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-03-11
Source: https://github.com/0xMiden/miden-vm/commit/a50a9abc9cf3ad61d7872e8cd4e43c28f66eecd0
Type: security-commit

## Details
fix(merkle): Remove potential overflow in to_scalar_index (#888)

This function previously had the potential to overflow for nodes at
depth 64. This commit now checks whether an overflow would occur, and
returns an error if this is the case.

## Patch
### CHANGELOG.md
```diff
@@ -19,6 +19,7 @@
 - Added `PublicKey::from_der()` for ECDSA public keys over secp256k1 ([#855](https://github.com/0xMiden/crypto/pull/855)).
 - [BREAKING] Removed `RpoRandomCoin` and `RpxRandomCoin` and introduced a Poseidon2-based `RandomCoin` ([#871](https://github.com/0xMiden/crypto/pull/871)).
 - Harden MerkleStore deserialization and fuzz coverage ([#878](https://github.com/0xMiden/crypto/pull/878)).
+- [BREAKING] Fixed `NodeIndex::to_scalar_index()` overflow at depth 64 by returning `Result<u64, MerkleError>` ([#865](https://github.com/0xMiden/crypto/issues/865)).
 
 ## 0.22.4 (2026-03-03)
 
```

### miden-crypto/src/merkle/index.rs
```diff
@@ -127,8 +127,16 @@ impl NodeIndex {
     /// Returns the scalar representation of the depth/position pair.
     ///
     /// It is computed as `2^depth + position`.
-    pub const fn to_scalar_index(&self) -> u64 {
-        (1 << self.depth as u64) + self.position
+    ///
+    /// # Errors
+    ///
+    /// - [`MerkleError::DepthTooBig`] if the depth is 64 or greater, as the resulting index would
+    ///   overflow.
+    pub const fn to_scalar_index(&self) -> Result<u64, MerkleError> {
+        if self.depth >= 64 {
+            return Err(MerkleError::DepthTooBig(self.depth as u64));
+        }
+        Ok((1u64 << self.depth as u64) + self.position)
     }
 
     /// Returns the depth of the current instance.
@@ -300,5 +308,55 @@ mod tests {
                 index.move_up();
             }
         }
+
+        #[test]
+        fn to_scalar_index_succeeds_for_depth_lt_64(depth in 0u8..64, position_bits in 0u64..u64::MAX) {
+            let position = if depth == 0 { 0 } else { position_bits % (1u64 << depth) };
+            let index = NodeIndex::new(depth, position).unwrap();
+            assert!(index.to_scalar_index().is_ok());
+        }
+    }
+
+    #[test]
+    fn test_to_scalar_index_depth_64_returns_error() {
+        let index = NodeIndex::new(64, 0).unwrap();
+        assert_matches!(index.to_scalar_index(), Err(MerkleError::DepthTooBig(64)));
+
+        let index = NodeIndex::new(64, u64::MAX).unwrap();
+        assert_matches!(index.to_scalar_index(), Err(MerkleError::DepthTooBig(64)));
+    }
+
+    #[test]
+    fn test_to_scalar_index_known_values() {
+        // Root's children: depth=1, pos=0 → scalar 2; depth=1, pos=1 → scalar 3
+        assert_eq!(NodeIndex::make(1, 0).to_scalar_index().unwrap(), 2);
+        assert_eq!(NodeIndex::make(1, 1).to_scalar_index().unwrap(), 3);
+
+        // depth=2: scalars 4,5,6,7
+        assert_eq!(NodeIndex::make(2, 0).to_scalar_index().unwrap(), 4);
+        assert_eq!(NodeIndex::make(2, 3).to_scalar_index().unwrap(), 7);
+
+        // depth=3: scalars 8..15
+        assert_eq!(NodeIndex::make(3, 0).to_scalar_index().unwrap(), 8);
+        assert_eq!(NodeIndex::make(3, 7).to_scalar_index().unwrap(), 15);
+    }
+
+    #[test]
+    fn test_to_scalar_index_depth_63_max_position() {
+        // 2^63 + (2^63 - 1) = 2^64 - 1 = u64::MAX
+        let index = NodeIndex::new(63, (1u64 << 63) - 1).unwrap();
+        assert_eq!(index.to_scalar_index().unwrap(), u64::MAX);
+    }
+
+    #[test]
+    fn test_to_scalar_index_boundary_depths() {
+        // depth 0 (root): scalar = 1 + 0 = 1
+        assert_eq!(NodeIndex::make(0, 0).to_scalar_index().unwrap(), 1);
+
+        // depth 62, position 0: scalar = 2^62
+        assert_eq!(NodeIndex::make(62, 0).to_scalar_index().unwrap(), 1u64 << 62);
+
+        // depth 63, position 0: scalar = 2^63
+        assert_eq!(NodeIndex::make(63, 0).to_scalar_index().unwrap(), 1u64 << 63);
     }
 }
```

### miden-crypto/src/merkle/merkle_tree.rs
```diff
@@ -88,7 +88,7 @@ impl MerkleTree {
             return Err(MerkleError::DepthTooBig(index.depth() as u64));
         }
 
-        let pos = index.to_scalar_index() as usize;
+        let pos = index.to_scalar_index()? as usize;
         Ok(self.nodes[pos])
     }
 
@@ -160,13 +160,13 @@ impl MerkleTree {
         let pairs: &'a [[Word; 2]] = unsafe { slice::from_raw_parts(ptr, n) };
 
         // update the current node
-        let pos = index.to_scalar_index() as usize;
+        let pos = index.to_scalar_index()? as usize;
         self.nodes[pos] = value;
 
         // traverse to the root, updating each node with the merged values of its parents
         for _ in 0..index.depth() {
             index.move_up();
-            let pos = index.to_scalar_index() as usize;
+            let pos = index.to_scalar_index()? as usize;
             let value = Poseidon2::merge(&pairs[pos]);
             self.nodes[pos] = value;
         }
```
