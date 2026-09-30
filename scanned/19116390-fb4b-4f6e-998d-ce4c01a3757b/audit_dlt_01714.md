# [?] sp-trie: correctly avoid panicking when decoding bad compact proofs (#6502)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2024-11-19
Source: https://github.com/paritytech/polkadot-sdk/commit/5e8348f03f49cc32ad48912e186c04b0f1212b16
Type: security-commit

## Details
sp-trie: correctly avoid panicking when decoding bad compact proofs (#6502)

# Description

Opening another PR because I added a test to check for my fix pushed in
#6486 and realized that for some reason I completely forgot how to code
and did not fix the underlying issue, since out-of-bounds indexing could
still happen even with the check I added. This one should fix that and,
as an added bonus, has a simple test used as an integrity check to make
sure future changes don't accidently revert this fix.

Now `sp-trie` should definitely not panic when faced with bad
`CompactProof`s. Sorry about that 😅

This, like #6486, is related to issue #6485

## Integration

No changes have to be done downstream, and as such the version bump
should be minor.

---------

Co-authored-by: Bastian Köcher <git@kchr.de>

## Patch
### prdoc/pr_6502.prdoc
```diff
@@ -0,0 +1,10 @@
+title: "sp-trie: correctly avoid panicking when decoding bad compact proofs"
+
+doc:
+  - audience: "Runtime Dev"
+    description: |
+      "Fixed the check introduced in [PR #6486](https://github.com/paritytech/polkadot-sdk/pull/6486). Now `sp-trie` correctly avoids panicking when decoding bad compact proofs."
+
+crates:
+- name: sp-trie
+  bump: patch
```

### substrate/primitives/trie/src/node_codec.rs
```diff
@@ -110,8 +110,8 @@ where
 			NodeHeader::Null => Ok(NodePlan::Empty),
 			NodeHeader::HashedValueBranch(nibble_count) | NodeHeader::Branch(_, nibble_count) => {
 				let padding = nibble_count % nibble_ops::NIBBLE_PER_BYTE != 0;
-				// data should be at least the size of the offset
-				if data.len() < input.offset {
+				// data should be at least of size offset + 1
+				if data.len() < input.offset + 1 {
 					return Err(Error::BadFormat)
 				}
 				// check that the padding is valid (if any)
@@ -158,8 +158,8 @@ where
 			},
 			NodeHeader::HashedValueLeaf(nibble_count) | NodeHeader::Leaf(nibble_count) => {
 				let padding = nibble_count % nibble_ops::NIBBLE_PER_BYTE != 0;
-				// data should be at least the size of the offset
-				if data.len() < input.offset {
+				// data should be at least of size offset + 1
+				if data.len() < input.offset + 1 {
 					return Err(Error::BadFormat)
 				}
 				// check that the padding is valid (if any)
```

### substrate/primitives/trie/src/storage_proof.rs
```diff
@@ -232,7 +232,8 @@ pub mod tests {
 	use super::*;
 	use crate::{tests::create_storage_proof, StorageProof};
 
-	type Layout = crate::LayoutV1<sp_core::Blake2Hasher>;
+	type Hasher = sp_core::Blake2Hasher;
+	type Layout = crate::LayoutV1<Hasher>;
 
 	const TEST_DATA: &[(&[u8], &[u8])] =
 		&[(b"key1", &[1; 64]), (b"key2", &[2; 64]), (b"key3", &[3; 64]), (b"key11", &[4; 64])];
@@ -245,4 +246,11 @@ pub mod tests {
 			Err(StorageProofError::DuplicateNodes)
 		));
 	}
+
+	#[test]
+	fn invalid_compact_proof_does_not_panic_when_decoding() {
+		let invalid_proof = CompactProof { encoded_nodes: vec![vec![135]] };
+		let result = invalid_proof.to_memory_db::<Hasher>(None);
+		assert!(result.is_err());
+	}
 }
```
