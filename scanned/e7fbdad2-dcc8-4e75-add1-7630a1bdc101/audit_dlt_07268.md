# [?] sp-trie: minor fix to avoid possible panic during node decoding (#6486)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2024-11-15
Source: https://github.com/paritytech/polkadot-sdk/commit/a77940bac783108fcae783c553528c8d5328e5b2
Type: security-commit

## Details
sp-trie: minor fix to avoid possible panic during node decoding (#6486)

# Description

This PR is a simple fix consisting of adding a check to the process of
decoding nodes of a storage proof to avoid panicking when receiving
badly-constructed proofs, returning an error instead.

This would close #6485

## Integration

No changes have to be done downstream, and as such the version bump
should be minor.

---------

Co-authored-by: Bastian Köcher <git@kchr.de>

## Patch
### prdoc/pr_6486.prdoc
```diff
@@ -0,0 +1,10 @@
+title: "sp-trie: minor fix to avoid panic on badly-constructed proof"
+
+doc:
+  - audience: ["Runtime Dev", "Runtime User"]
+    description: |
+      "Added a check when decoding encoded proof nodes in `sp-trie` to avoid panicking when receiving a badly constructed proof, instead erroring out."
+
+crates:
+- name: sp-trie
+  bump: patch
```

### substrate/primitives/trie/src/node_codec.rs
```diff
@@ -110,6 +110,10 @@ where
 			NodeHeader::Null => Ok(NodePlan::Empty),
 			NodeHeader::HashedValueBranch(nibble_count) | NodeHeader::Branch(_, nibble_count) => {
 				let padding = nibble_count % nibble_ops::NIBBLE_PER_BYTE != 0;
+				// data should be at least the size of the offset
+				if data.len() < input.offset {
+					return Err(Error::BadFormat)
+				}
 				// check that the padding is valid (if any)
 				if padding && nibble_ops::pad_left(data[input.offset]) != 0 {
 					return Err(Error::BadFormat)
@@ -154,6 +158,10 @@ where
 			},
 			NodeHeader::HashedValueLeaf(nibble_count) | NodeHeader::Leaf(nibble_count) => {
 				let padding = nibble_count % nibble_ops::NIBBLE_PER_BYTE != 0;
+				// data should be at least the size of the offset
+				if data.len() < input.offset {
+					return Err(Error::BadFormat)
+				}
 				// check that the padding is valid (if any)
 				if padding && nibble_ops::pad_left(data[input.offset]) != 0 {
 					return Err(Error::BadFormat)
```
