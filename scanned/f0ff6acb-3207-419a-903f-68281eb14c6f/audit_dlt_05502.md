# [?] account-compression: fix for a stack overflow issue on macro usage (#6827)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2024-06-24
Source: https://github.com/solana-labs/solana-program-library/commit/d85ea9ff0573cd82c9245965a55f379b4dc263bc
Type: security-commit

## Details
account-compression: fix for a stack overflow issue on macro usage (#6827)

* account-compression: fix for a stack overflow issue on macro usage

* clippy: removed unnecessary references

* update cmt tests

* fix rustfmt

* bump spl-concurrent-merkle-tree to 0.3.0 for API changes

---------

Co-authored-by: ngundotra <noah@gundotra.org>
Co-authored-by: Noah Gundotra <ngundotra@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -6907,7 +6907,7 @@ dependencies = [
 
 [[package]]
 name = "spl-concurrent-merkle-tree"
-version = "0.2.0"
+version = "0.3.0"
 dependencies = [
  "bytemuck",
  "rand 0.8.5",
```

### account-compression/programs/account-compression/Cargo.toml
```diff
@@ -21,8 +21,8 @@ default = []
 anchor-lang = "0.29.0"
 bytemuck = "1.13"
 solana-program = ">=1.18.11,<=2"
-spl-concurrent-merkle-tree = { version = "0.2.0", path = "../../../libraries/concurrent-merkle-tree", features = [
-  "sol-log",
+spl-concurrent-merkle-tree = { version = "0.3.0", path = "../../../libraries/concurrent-merkle-tree", features = [
+    "sol-log",
 ] }
 spl-noop = { version = "0.2.0", path = "../noop", features = ["no-entrypoint"] }
 
```

### account-compression/programs/account-compression/src/concurrent_tree_wrapper.rs
```diff
@@ -0,0 +1,65 @@
+//! This module provides a wrapper around the `ConcurrentMerkleTree` struct from
+//! the `spl_concurrent_merkle_tree` crate. It provides a set of functions that
+//! can be called from the Anchor program to interact with the tree.
+//! The functions are used to initialize the tree, set a leaf, fill empty or
+//! append a leaf, and prove a leaf. As the tree is generic over the depth and
+//! buffer size, the functions are implemented using macros that infer the depth
+//! and buffer size from the header information stored on-chain. Usage of the
+//! macros directly is discouraged, as they have huge match statements with
+//! every case taking it's own stack frame. Instead, use the exported functions
+//! from this module and refenrece or Box the arguments to the functions to
+//! avoid the stack frame explosion.
+
+pub use crate::error::AccountCompressionError;
+/// Exported for Anchor / Solita
+pub use spl_concurrent_merkle_tree::{
+    concurrent_merkle_tree::{
+        ConcurrentMerkleTree, FillEmptyOrAppendArgs, InitializeWithRootArgs, ProveLeafArgs,
+        SetLeafArgs,
+    },
+    error::ConcurrentMerkleTreeError,
+    node::Node,
+    node::EMPTY,
+};
+use {
+    crate::{
+        events::ChangeLogEvent, macros::*, state::ConcurrentMerkleTreeHeader, zero_copy::ZeroCopy,
+    },
+    anchor_lang::prelude::*,
+};
+
+pub fn merkle_tree_initialize_with_root(
+    header: &ConcurrentMerkleTreeHeader,
+    tree_id: Pubkey,
+    tree_bytes: &mut [u8],
+    args: &InitializeWithRootArgs,
+) -> Result<Box<ChangeLogEvent>> {
+    merkle_tree_apply_fn_mut!(header, tree_id, tree_bytes, initialize_with_root, args)
+}
+
+pub fn merkle_tree_set_leaf(
+    header: &ConcurrentMerkleTreeHeader,
+    tree_id: Pubkey,
+    tree_bytes: &mut [u8],
+    args: &SetLeafArgs,
+) -> Result<Box<ChangeLogEvent>> {
+    merkle_tree_apply_fn_mut!(header, tree_id, tree_bytes, set_leaf, args)
+}
+
+pub fn merkle_tree_fill_empty_or_append(
+    header: &ConcurrentMerkleTreeHeader,
+    tree_id: Pubkey,
+    tree_bytes: &mut [u8],
+    args: &FillEmptyOrAppendArgs,
+) -> Result<Box<ChangeLogEvent>> {
+    merkle_tree_apply_fn_mut!(header, tree_id, tree_bytes, fill_empty_or_append, args)
+}
+
+pub fn merkle_tree_prove_leaf(
+    header: &ConcurrentMerkleTreeHeader,
+    tree_id: Pubkey,
+    tree_bytes: &[u8],
+    args: &ProveLeafArgs,
+) -> Result<Box<ChangeLogEvent>> {
+    merkle_tree_apply_fn!(header, tree_id, tree_bytes, prove_leaf, args)
+}
```

### account-compression/programs/account-compression/src/lib.rs
```diff
@@ -29,6 +29,7 @@ use anchor_lang::{
 use borsh::{BorshDeserialize, BorshSerialize};
 
 pub mod canopy;
+pub mod concurrent_tree_wrapper;
 pub mod error;
 pub mod events;
 #[macro_use]
@@ -40,6 +41,7 @@ pub mod zero_copy;
 pub use crate::noop::{wrap_application_data_v1, Noop};
 
 use crate::canopy::{fill_in_proof_from_canopy, update_canopy};
+use crate::concurrent_tree_wrapper::*;
 pub use crate::error::AccountCompressionError;
 pub use crate::events::{AccountCompressionEvent, ChangeLogEvent};
 use crate::noop::wrap_event;
@@ -50,7 +52,9 @@ use crate::zero_copy::ZeroCopy;
 
 /// Exported for Anchor / Solita
 pub use spl_concurrent_merkle_tree::{
-    concurrent_merkle_tree::ConcurrentMerkleTree, error::ConcurrentMerkleTreeError, node::Node,
+    concurrent_merkle_tree::{ConcurrentMerkleTree, FillEmptyOrAppendArgs},
+    error::ConcurrentMerkleTreeError,
+    node::Node,
 };
 
 declare_id!("cmtDvXumGCrqC1Age74AVPhSRVXJMd8PJS91L8KbNCK");
@@ -270,17 +274,15 @@ pub mod spl_account_compression {
         fill_in_proof_from_canopy(canopy_bytes, header.get_max_depth(), index, &mut proof)?;
         let id = ctx.accounts.merkle_tree.key();
         // A call is made to ConcurrentMerkleTree::set_leaf(root, previous_leaf, new_leaf, proof, index)
-        let change_log_event = merkle_tree_apply_fn_mut!(
-            header,
-            id,
-            tree_bytes,
-            set_leaf,
-            root,
+        let args = &SetLeafArgs {
+            current_root: root,
             previous_leaf,
             new_leaf,
-            &proof,
+            proof_vec: proof,
             index,
-        )?;
+        };
+        let change_log_event = merkle_tree_set_leaf(&header, id, tree_bytes, args)?;
+
         update_canopy(
             canopy_bytes,
             header.get_max_depth(),
@@ -347,7 +349,14 @@ pub mod spl_account_compression {
         fill_in_proof_from_canopy(canopy_bytes, header.get_max_depth(), index, &mut proof)?;
         let id = ctx.accounts.merkle_tree.key();
 
-        merkle_tree_apply_fn!(header, id, tree_bytes, prove_leaf, root, leaf, &proof, index)?;
+        let args = &ProveLeafArgs {
+            current_root: root,
+            leaf,
+            proof_vec: proof,
+            index,
+        };
+        merkle_tree_prove_leaf(&header, id, tree_bytes, args)?;
+
         Ok(())
     }
 
@@ -418,16 +427,14 @@ pub mod spl_account_compression {
         fill_in_proof_from_canopy(canopy_bytes, header.get_max_depth(), index, &mut proof)?;
         // A call is made to ConcurrentMerkleTree::fill_empty_or_append
         let id = ctx.accounts.merkle_tree.key();
-        let change_log_event = merkle_tree_apply_fn_mut!(
-            header,
-            id,
-            tree_bytes,
-            fill_empty_or_append,
-            root,
+        let args = &FillEmptyOrAppendArgs {
+            current_root: root,
             leaf,
-            &proof,
+            proof_vec: proof,
             index,
-        )?;
+        };
+        let change_log_event = merkle_tree_fill_empty_or_append(&header, id, tree_bytes, args)?;
+
         update_canopy(
             canopy_bytes,
             header.get_max_depth(),
```

### account-compression/programs/account-compression/src/macros.rs
```diff
@@ -4,8 +4,8 @@ enum TreeLoad {
     Mutable,
 }
 
-/// This macro applies functions on a ConcurrentMerkleT:ee and emits leaf information
-/// needed to sync the merkle tree state with off-chain indexers.
+/// This macro applies functions on a ConcurrentMerkleT:ee and emits leaf
+/// information needed to sync the merkle tree state with off-chain indexers.
 #[macro_export]
 macro_rules! _merkle_tree_depth_size_apply_fn {
     ($max_depth:literal, $max_size:literal, $id:ident, $bytes:ident, $func:ident, TreeLoad::Mutable, $($arg:tt)*)
@@ -118,3 +118,8 @@ macro_rules! merkle_tree_apply_fn {
         _merkle_tree_apply_fn!($header, $id, $bytes, $func, TreeLoad::Immutable, $($arg)*)
     };
 }
+
+pub(crate) use {
+    _merkle_tree_apply_fn, _merkle_tree_depth_size_apply_fn, merkle_tree_apply_fn,
+    merkle_tree_apply_fn_mut,
+};
```

### libraries/concurrent-merkle-tree/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "spl-concurrent-merkle-tree"
-version = "0.2.0"
+version = "0.3.0"
 description = "Solana Program Library Concurrent Merkle Tree"
 authors = ["Solana Labs Maintainers <maintainers@solanalabs.com>"]
 repository = "https://github.com/solana-labs/solana-program-library"
@@ -9,7 +9,7 @@ edition = "2021"
 
 [features]
 log = []
-sol-log = [ "log" ]
+sol-log = ["log"]
 
 [dependencies]
 solana-program = "1.16"
```

### libraries/concurrent-merkle-tree/src/concurrent_merkle_tree.rs
```diff
@@ -51,6 +51,15 @@ fn check_leaf_index(leaf_index: u32, max_depth: usize) -> Result<(), ConcurrentM
 /// [append](ConcurrentMerkleTree::append) operations, which do not require any
 /// proofs to be passed. This is accomplished by keeping track of the
 /// proof to the rightmost leaf in the tree (`rightmost_proof`).
+///
+/// The `ConcurrentMerkleTree` is a generic struct that may be interacted with
+/// using macros. Those macros may wrap up the construction and both mutable and
+/// immutable calls to the `ConcurrentMerkleTree` struct. If the macro contains
+/// a big match statement over different sizes of a tree and buffer, it might
+/// create a huge stack footprint. This in turn might lead to a stack overflow
+/// given the max stack offset of just 4kb. In order to minimize the stack frame
+/// size, the arguments for the `ConcurrentMerkleTree` methods that contain the
+/// proofs are passed as references to structs.
 #[repr(C)]
 #[derive(Copy, Clone)]
 pub struct ConcurrentMerkleTree<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize> {
@@ -87,6 +96,40 @@ impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize> Default
     }
 }
 
+/// Arguments structure for initializing a tree with a root.
+pub struct InitializeWithRootArgs {
+    pub root: Node,
+    pub rightmost_leaf: Node,
+    pub proof_vec: Vec<Node>,
+    pub index: u32,
+}
+
+/// Arguments structure for setting a leaf in the tree.
+pub struct SetLeafArgs {
+    pub current_root: Node,
+    pub previous_leaf: Node,
+    pub new_leaf: Node,
+    pub proof_vec: Vec<Node>,
+    pub index: u32,
+}
+
+/// Arguments structure for filling an empty leaf or appending a new leaf to the
+/// tree.
+pub struct FillEmptyOrAppendArgs {
+    pub current_root: Node,
+    pub leaf: Node,
+    pub proof_vec: Vec<Node>,
+    pub index: u32,
+}
+
+/// Arguments structure for proving a leaf in the tree.
+pub struct ProveLeafArgs {
+    pub current_root: Node,
+    pub leaf: Node,
+    pub proof_vec: Vec<Node>,
+    pub index: u32,
+}
+
 impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize>
     ConcurrentMerkleTree<MAX_DEPTH, MAX_BUFFER_SIZE>
 {
@@ -132,35 +175,32 @@ impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize>
     /// other applications from indexing the leaf data stored in this tree.
     pub fn initialize_with_root(
         &mut self,
-        root: Node,
-        rightmost_leaf: Node,
-        proof_vec: &[Node],
-        index: u32,
+        args: &InitializeWithRootArgs,
     ) -> Result<Node, ConcurrentMerkleTreeError> {
         check_bounds(MAX_DEPTH, MAX_BUFFER_SIZE);
-        check_leaf_index(index, MAX_DEPTH)?;
+        check_leaf_index(args.index, MAX_DEPTH)?;
 
         if self.is_initialized() {
             return Err(ConcurrentMerkleTreeError::TreeAlreadyInitialized);
         }
         let mut proof: [Node; MAX_DEPTH] = [Node::default(); MAX_DEPTH];
-        proof.copy_from_slice(proof_vec);
+        proof.copy_from_slice(&args.proof_vec);
         let rightmost_proof = Path {
             proof,
-            index: index + 1,
-            leaf: rightmost_leaf,
+            index: args.index + 1,
+            leaf: args.rightmost_leaf,
             _padding: 0,
         };
-        self.change_logs[0].root = root;
+        self.change_logs[0].root = args.root;
         self.sequence_number = 1;
         self.active_index = 0;
         self.buffer_size = 1;
         self.rightmost_proof = rightmost_proof;
-        if root != recompute(rightmost_leaf, &proof, index) {
+        if args.root != recompute(args.rightmost_leaf, &proof, args.index) {
             solana_logging!("Proof failed to verify");
             return Err(ConcurrentMerkleTreeError::InvalidProof);
         }
-        Ok(root)
+        Ok(args.root)
     }
 
     /// Errors if one of the leaves of the current merkle tree is non-EMPTY
@@ -200,31 +240,25 @@ impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize>
     /// Note: this is *not* the same as verifying that a (proof, leaf)
     /// combination is valid for the given root. That functionality
     /// is provided by `check_valid_proof`.
-    pub fn prove_leaf(
-        &self,
-        current_root: Node,
-        leaf: Node,
-        proof_vec: &[Node],
-        leaf_index: u32,
-    ) -> Result<(), ConcurrentMerkleTreeError> {
+    pub fn prove_leaf(&self, args: &ProveLeafArgs) -> Result<(), ConcurrentMerkleTreeError> {
         check_bounds(MAX_DEPTH, MAX_BUFFER_SIZE);
-        check_leaf_index(leaf_index, MAX_DEPTH)?;
+        check_leaf_index(args.index, MAX_DEPTH)?;
         if !self.is_initialized() {
             return Err(ConcurrentMerkleTreeError::TreeNotInitialized);
         }
 
-        if leaf_index > self.rightmost_proof.index {
+        if args.index > self.rightmost_proof.index {
             solana_logging!(
                 "Received an index larger than the rightmost index {} > {}",
-                leaf_index,
+                args.index,
                 self.rightmost_proof.index
             );
             Err(ConcurrentMerkleTreeError::LeafIndexOutOfBounds)
         } else {
             let mut proof: [Node; MAX_DEPTH] = [Node::default(); MAX_DEPTH];
-            fill_in_proof::<MAX_DEPTH>(proof_vec, &mut proof);
+            fill_in_proof::<MAX_DEPTH>(&args.proof_vec, &mut proof);
             let valid_root =
-                self.check_valid_leaf(current_root, leaf, &mut proof, leaf_index, true)?;
+                self.check_valid_leaf(args.current_root, args.leaf, &mut proof, args.index, true)?;
             if !valid_root {
                 solana_logging!("Proof failed to verify");
                 return Err(ConcurrentMerkleTreeError::InvalidProof);
@@ -313,25 +347,29 @@ impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize>
     /// otherwise it will `append` the new leaf.
     pub fn fill_empty_or_append(
         &mut self,
-        current_root: Node,
-        leaf: Node,
-        proof_vec: &[Node],
-        index: u32,
+        args: &FillEmptyOrAppendArgs,
     ) -> Result<Node, ConcurrentMerkleTreeError> {
         check_bounds(MAX_DEPTH, MAX_BUFFER_SIZE);
-        check_leaf_index(index, MAX_DEPTH)?;
+        check_leaf_index(args.index, MAX_DEPTH)?;
         if !self.is_initialized() {
             return Err(ConcurrentMerkleTreeError::TreeNotInitialized);
         }
 
         let mut proof: [Node; MAX_DEPTH] = [Node::default(); MAX_DEPTH];
-        fill_in_proof::<MAX_DEPTH>(proof_vec, &mut proof);
+        fill_in_proof::<MAX_DEPTH>(&args.proof_vec, &mut proof);
 
         log_compute!();
-        match self.try_apply_proof(current_root, EMPTY, leaf, &mut proof, index, false) {
+        match self.try_apply_proof(
+            args.current_root,
+            EMPTY,
+            args.leaf,
+            &mut proof,
+            args.index,
+            false,
+        ) {
             Ok(new_root) => Ok(new_root),
             Err(error) => match error {
-                ConcurrentMerkleTreeError::LeafContentsModified => self.append(leaf),
+                ConcurrentMerkleTreeError::LeafContentsModified => self.append(args.leaf),
                 _ => Err(error),
             },
         }
@@ -340,33 +378,26 @@ impl<const MAX_DEPTH: usize, const MAX_BUFFER_SIZE: usize>
     /// This method will update the leaf at `index`.
     ///
     /// However if the proof cannot be verified, this method will fail.
-    pub fn set_leaf(
-        &mut self,
-        current_root: Node,
-        previous_leaf: Node,
-        new_leaf: Node,
-        proof_vec: &[Node],
-        index: u32,
-    ) -> Result<Node, ConcurrentMerkleTreeError> {
+    pub fn set_leaf(&mut self, args: &SetLeafArgs) -> Result<Node, ConcurrentMerkleTreeError> {
         check_bounds(MAX_DEPTH, MAX_BUFFER_SIZE);
-        check_leaf_index(index, MAX_DEPTH)?;
+        check_leaf_index(args.index, MAX_DEPTH)?;
         if !self.is_initialized() {
             return Err(ConcurrentMerkleTreeError::TreeNotInitialized);
         }
 
-        if index > self.rightmost_proof.index {
+        if args.index > self.rightmost_proof.index {
             Err(ConcurrentMerkleTreeError::LeafIndexOutOfBounds)
         } else {
             let mut proof: [Node; MAX_DEPTH] = [Node::default(); MAX_DEPTH];
-            fill_in_proof::<MAX_DEPTH>(proof_vec, &mut proof);
+            fill_in_proof::<MAX_DEPTH>(&args.proof_vec, &mut proof);
 
             log_compute!();
             self.try_apply_proof(
-                current_root,
-                previous_leaf,
-                new_leaf,
+                args.current_root,
+                args.previous_leaf,
+                args.new_leaf,
                 &mut proof,
-                index,
+                args.index,
                 true,
             )
         }
```

### libraries/concurrent-merkle-tree/tests/tests.rs
```diff
@@ -2,7 +2,10 @@
 use {
     rand::{self, thread_rng, Rng},
     spl_concurrent_merkle_tree::{
-        concurrent_merkle_tree::ConcurrentMerkleTree,
+        concurrent_merkle_tree::{
+            ConcurrentMerkleTree, FillEmptyOrAppendArgs, InitializeWithRootArgs, ProveLeafArgs,
+            SetLeafArgs,
+        },
         error::ConcurrentMerkleTreeError,
         node::{Node, EMPTY},
     },
@@ -56,36 +59,33 @@ async fn test_bypass_initialize() {
 
     assert_eq!(
         ConcurrentMerkleTreeError::TreeNotInitialized,
-        cmt.set_leaf(
-            off_chain_tree.get_root(),
-            [0; 32],
-            leaf,
-            &off_chain_tree.get_proof_of_leaf(0),
-            0
-        )
-        .unwrap_err(),
+        cmt.set_leaf(&SetLeafArgs {
+            current_root: off_chain_tree.get_root(),
+            previous_leaf: [0; 32],
+            new_leaf: leaf,
+            proof_vec: off_chain_tree.get_proof_of_leaf(0),
+            index: 0
+        },)
+            .unwrap_err(),
         "Expected TreeNotInitialized error when setting a leaf on an uninitialized tree"
     );
 
     assert_eq!(
         ConcurrentMerkleTreeError::TreeNotInitialized,
-        cmt.prove_leaf(
-            off_chain_tree.get_root(),
+        cmt.prove_leaf(&ProveLeafArgs {
+            current_root: off_chain_tree.get_root(),
             leaf,
-            &off_chain_tree.get_proof_of_leaf(0),
-            0,
-        )
+            proof_vec: off_chain_tree.get_proof_of_leaf(0),
+            index: 0
+        })
         .unwrap_err(),
         "Expected TreeNotInitialized error when proving a leaf exists on an uninitialized tree"
     );
 
     assert_eq!(
         ConcurrentMerkleTreeError::TreeNotInitialized,
         cmt.fill_empty_or_append(
-            off_chain_tree.get_root(),
-            leaf,
-            &off_chain_tree.get_proof_of_leaf(0),
-            0,
+            &FillEmptyOrAppendArgs { current_root: off_chain_tree.get_root(), leaf, proof_vec: off_chain_tree.get_proof_of_leaf(0), index: 0 }
         )
         .unwrap_err(),
         "Expected TreeNotInitialized error when filling an empty leaf or appending to uninitialized tree"
@@ -129,12 +129,12 @@ async fn test_prove_leaf() {
 
     // Test that all leaves can be verified
     for leaf_index in 0..(1 << DEPTH) {
-        cmt.prove_leaf(
-            off_chain_tree.get_root(),
-            off_chain_tree.get_leaf(leaf_index),
-            &off_chain_tree.get_proof_of_leaf(leaf_index),
-            leaf_index as u32,
-        )
+        cmt.prove_leaf(&ProveLeafArgs {
+            current_root: off_chain_tree.get_root(),
+            leaf: off_chain_tree.get_leaf(leaf_index),
+            proof_vec: off_chain_tree.get_proof_of_leaf(leaf_index),
+            index: leaf_index as u32,
+        })
         .unwrap();
     }
 
@@ -156,19 +156,24 @@ async fn test_prove_leaf() {
                 random_leaf_idx = rng.gen_range(0..1 << DEPTH);
             }
 
-            cmt.set_leaf(
-                off_chain_tree.get_root(),
-                off_chain_tree.get_leaf(random_leaf_idx),
+            cmt.set_leaf(&SetLeafArgs {
+                current_root: off_chain_tree.get_root(),
+                previous_leaf: off_chain_tree.get_leaf(random_leaf_idx),
                 new_leaf,
-                &off_chain_tree.get_proof_of_leaf(random_leaf_idx),
-                random_leaf_idx as u32,
-            )
+                proof_vec: off_chain_tree.get_proof_of_leaf(random_leaf_idx),
+                index: random_leaf_idx as u32,
+            })
             .unwrap();
             off_chain_tree.add_leaf(new_leaf, random_leaf_idx);
 
             // Assert that we can still prove existence of our mostly unused leaf
-            cmt.prove_leaf(root, leaf, &old_proof, leaf_idx as u32)
-                .unwrap();
+            cmt.prove_leaf(&ProveLeafArgs {
+                current_root: root,
+                leaf,
+                proof_vec: old_proof.clone(),
+                index: leaf_idx as u32,
+            })
+            .unwrap();
         }
     }
 }
@@ -183,12 +188,12 @@ async fn test_initialize_with_root() {
     }
 
     let last_leaf_idx = tree.leaf_nodes.len() - 1;
-    cmt.initialize_with_root(
-        tree.get_root(),
-        tree.get_leaf(last_leaf_idx),
-        &tree.get_proof_of_leaf(last_leaf_idx),
-        last_leaf_idx as u32,
-    )
+    cmt.initialize_with_root(&InitializeWithRootArgs {
+        root: tree.get_root(),
+        rightmost_leaf: tree.get_leaf(last_leaf_idx),
+        proof_vec: tree.get_proof_of_leaf(last_leaf_idx),
+        index: last_leaf_idx as u32,
+    })
     .unwrap();
 
     assert_eq!(
@@ -198,12 +203,14 @@ async fn test_initialize_with_root() {
     );
 
     // Check that reinitialization fails
-    if let Err(ConcurrentMerkleTreeError::TreeAlreadyInitialized) = cmt.initialize_with_root(
-        tree.get_root(),
-        tree.get_leaf(last_leaf_idx),
-        &tree.get_proof_of_leaf(last_leaf_idx),
-        last_leaf_idx as u32,
-    ) {
+    if let Err(ConcurrentMerkleTreeError::TreeAlreadyInitialized) =
+        cmt.initialize_with_root(&InitializeWithRootArgs {
+            root: tree.get_root(),
+            rightmost_leaf: tree.get_leaf(last_leaf_idx),
+            proof_vec: tree.get_proof_of_leaf(last_leaf_idx),
+            index: last_leaf_idx as u32,
+        })
+    {
         println!("Reinitialization with root successfully prevented");
     } else {
         panic!("Tree should not be able to be reinitialized");
@@ -228,12 +235,25 @@ async fn test_leaf_contents_modified() {
     // Update leaf to be something else
     let new_leaf_0 = rng.gen::<[u8; 32]>();
     tree.add_leaf(leaf, 0);
-    cmt.set_leaf(root, leaf, new_leaf_0, &proof, 0_u32).unwrap();
+    cmt.set_leaf(&SetLeafArgs {
+        current_root: root,
+        previous_leaf: leaf,
+        new_leaf: new_leaf_0,
+        proof_vec: proof.clone(),
+        index: 0_u32,
+    })
+    .unwrap();
 
     // Should fail to replace same leaf using outdated info
     let new_leaf_1 = rng.gen::<[u8; 32]>();
     tree.add_leaf(leaf, 0);
-    match cmt.set_leaf(root, leaf, new_leaf_1, &proof, 0_u32) {
+    match cmt.set_leaf(&SetLeafArgs {
+        current_root: root,
+        previous_leaf: leaf,
+        new_leaf: new_leaf_1,
+        proof_vec: proof,
+        index: 0u32,
+    }) {
         Ok(_) => {
             panic!("CMT should fail when replacing leafs with outdated leaf proofs")
         }
@@ -263,13 +283,13 @@ async fn test_replaces() {
     // Replace leaves in order
     for i in 0..(1 << DEPTH) {
         let leaf = rng.gen::<[u8; 32]>();
-        cmt.set_leaf(
-            tree.get_root(),
-            tree.get_leaf(i),
-            leaf,
-            &tree.get_proof_of_leaf(i),
-            i as u32,
-        )
+        cmt.set_leaf(&SetLeafArgs {
+            current_root: tree.get_root(),
+            previous_leaf: tree.get_leaf(i),
+            new_leaf: leaf,
+            proof_vec: tree.get_proof_of_leaf(i),
+            index: i as u32,
+        })
         .unwrap();
         tree.add_leaf(leaf, i);
         assert_eq!(cmt.get_change_log().root, tree.get_root());
@@ -280,13 +300,13 @@ async fn test_replaces() {
     for _ in 0..(test_capacity) {
         let index = rng.gen_range(0..test_capacity) % (1 << DEPTH);
         let leaf = rng.gen::<[u8; 32]>();
-        cmt.set_leaf(
-            tree.get_root(),
-            tree.get_leaf(index),
-            leaf,
-            &tree.get_proof_of_leaf(index),
-            index as u32,
-        )
+        cmt.set_leaf(&SetLeafArgs {
+            current_root: tree.get_root(),
+            previous_leaf: tree.get_leaf(index),
+            new_leaf: leaf,
+            proof_vec: tree.get_proof_of_leaf(index),
+            index: index as u32,
+        })
         .unwrap();
         tree.add_leaf(leaf, index);
         assert_eq!(cmt.get_change_log().root, tree.get_root());
@@ -332,13 +352,13 @@ async fn test_mixed() {
         } else {
             let index = rng.gen_range(0..tree_size) % (tree_size);
             println!("{} replace {}", tree_size, index);
-            cmt.set_leaf(
-                tree.get_root(),
-                tree.get_leaf(index),
-                leaf,
-                &tree.get_proof_of_leaf(index),
-                index as u32,
-            )
+            cmt.set_leaf(&SetLeafArgs {
+                current_root: tree.get_root(),
+                previous_leaf: tree.get_leaf(index),
+                new_leaf: leaf,
+                proof_vec: tree.get_proof_of_leaf(index),
+                index: index as u32,
+            })
             .unwrap();
             tree.add_leaf(leaf, index);
         }
@@ -373,13 +393,13 @@ async fn test_append_bug_repro_1() {
     // Replace the rightmost leaf
     let leaf_0 = rng.gen::<[u8; 32]>();
     let index = 9;
-    cmt.set_leaf(
-        tree.get_root(),
-        tree.get_leaf(index),
-        leaf_0,
-        &tree.get_proof_of_leaf(index),
-        index as u32,
-    )
+    cmt.set_leaf(&SetLeafArgs {
+        current_root: tree.get_root(),
+        previous_leaf: tree.get_leaf(index),
+        new_leaf: leaf_0,
+        proof_vec: tree.get_proof_of_leaf(index),
+        index: index as u32,
+    })
     .unwrap();
     tree.add_leaf(leaf_0, index);
 
@@ -417,13 +437,13 @@ async fn test_append_bug_repro_2() {
     // Replace the rightmost leaf
     let mut leaf = rng.gen::<[u8; 32]>();
     let index = 10;
-    cmt.set_leaf(
-        tree.get_root(),
-        tree.get_leaf(index),
-        leaf,
-        &tree.get_proof_of_leaf(index),
-        index as u32,
-    )
+    cmt.set_leaf(&SetLeafArgs {
+        current_root: tree.get_root(),
+        previous_leaf: tree.get_leaf(index),
+        new_leaf: leaf,
+        proof_vec: tree.get_proof_of_leaf(index),
+        index: index as u32,
+    })
     .unwrap();
     tree.add_leaf(leaf, index);
     tree_size += 1;
@@ -473,13 +493,13 @@ async fn test_prove_tree_empty_incremental() {
             },
         }
 
-        cmt.set_leaf(
-            tree.get_root(),
-            tree.get_leaf(i),
-            EMPTY,
-            &tree.get_proof_of_leaf(i),
-            i as u32,
-        )
+        cmt.set_leaf(&SetLeafArgs {
+            current_root: tree.get_root(),
+            previous_leaf: tree.get_leaf(i),
+            new_leaf: EMPTY,
+            proof_vec: tree.get_proof_of_leaf(i),
+            index: i as u32,
+        })
         .unwrap();
         tree.add_leaf(EMPTY, i);
 
@@ -519,13 +539,13 @@ async fn test_prove_tree_empty_batched() {
     }
     // Remove random leaves
     for i in 0..tree_size - 1 {
-        cmt.set_leaf(
-            tree.get_root(),
-            tree.get_leaf(i),
-            EMPTY,
-            &tree.get_proof_of_leaf(i),
-            i as u32,
-        )
+        cmt.set_leaf(&SetLeafArgs {
+            current_root: tree.get_root(),
+            previous_leaf: tree.get_leaf(i),
+            new_leaf: EMPTY,
+            proof_vec: tree.get_proof_of_leaf(i),
+            index: i as u32,
+        })
         .unwrap();
         tree.add_leaf(EMPTY, i);
 
@@ -541,13 +561,13 @@ async fn test_prove_tree_empty_batched() {
             },
         }
     }
-    cmt.set_leaf(
-        tree.get_root(),
-        tree.get_leaf(tree_size - 1),
-        EMPTY,
-        &tree.get_proof_of_leaf(tree_size - 1),
-        (tree_size - 1) as u32,
-    )
+    cmt.set_leaf(&SetLeafArgs {
+        current_root: tree.get_root(),
+        previous_leaf: tree.get_leaf(tree_size - 1),
+        new_leaf: EMPTY,
+        proof_vec: tree.get_proof_of_leaf(tree_size - 1),
+        index: (tree_size - 1) as u32,
+    })
     .unwrap();
     tree.add_leaf(EMPTY, tree_size - 1);
 
```
