# [?] client/api: fix possible deadlock when comparing with itself (#6277)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2020-06-08
Source: https://github.com/paritytech/substrate/commit/4a560614ccc0bbf6ecd4e80784a9e9e9a06191e2
Type: security-commit

## Details
client/api: fix possible deadlock when comparing with itself (#6277)

## Patch
### client/api/src/in_mem.rs
```diff
@@ -19,6 +19,7 @@
 //! In memory client backend
 
 use std::collections::HashMap;
+use std::ptr;
 use std::sync::Arc;
 use parking_lot::RwLock;
 use sp_core::{
@@ -191,11 +192,19 @@ impl<Block: BlockT> Blockchain<Block> {
 
 	/// Compare this blockchain with another in-mem blockchain
 	pub fn equals_to(&self, other: &Self) -> bool {
+		// Check ptr equality first to avoid double read locks.
+		if ptr::eq(self, other) {
+			return true;
+		}
 		self.canon_equals_to(other) && self.storage.read().blocks == other.storage.read().blocks
 	}
 
 	/// Compare canonical chain to other canonical chain.
 	pub fn canon_equals_to(&self, other: &Self) -> bool {
+		// Check ptr equality first to avoid double read locks.
+		if ptr::eq(self, other) {
+			return true;
+		}
 		let this = self.storage.read();
 		let other = other.storage.read();
 			this.hashes == other.hashes
```
