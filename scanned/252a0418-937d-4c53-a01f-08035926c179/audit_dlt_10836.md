# [?] Merge pull request #7218 from brice-stacks/fix/cve-2012-2459

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-05-22
Source: https://github.com/stacks-network/stacks-core/commit/30629d416738a957be0727bdc1db6b409036147a
Type: security-commit

## Details
Merge pull request #7218 from brice-stacks/fix/cve-2012-2459

feat: make `verify-merkle-proof` more strict

## Patch
### changelog.d/verify-merkle-proof-padding-relocation.fixed
```diff
@@ -0,0 +1 @@
+Tightens the Clarity 6 `verify-merkle-proof` builtin so that it rejects CVE-2012-2459-style "inflated `tx-count`" forgeries that relocate the last real leaf of an odd-sized tree into the duplicated-padding region (e.g. presenting the same real Bitcoin tx as `(tx-index 3, tx-count 4)` against the merkle root of a 3-tx block).
```

### clarity/src/vm/docs/mod.rs
```diff
@@ -1435,8 +1435,11 @@ function returns `true` iff hashing pairwise up the tree in the order described
 
 `tx-count` pins down the canonical Bitcoin tree shape and is required to defend against
 CVE-2012-2459-style attacks where an intermediate node in an odd-row-padded tree could
-otherwise be passed off as a leaf. The function rejects any proof whose path length doesn't
-match `ceil(log2(tx-count))` and any `tx-index` not less than `tx-count`.
+otherwise be passed off as a leaf, or where the last real leaf of an odd-sized tree
+could be relocated into the duplicated-padding region by inflating `tx-count`. The
+function rejects any proof whose path length doesn't match `ceil(log2(tx-count))`, any
+`tx-index` not less than `tx-count`, and any sibling whose value is inconsistent with the
+canonical tree shape implied by the supplied `tx-count`.
 
 All 32-byte hashes (leaf, root, siblings) are passed in *internal* (raw) byte order, not
 the display (reversed) order conventionally used for Bitcoin txids and block hashes. The
```

### clarity/src/vm/functions/bitcoin.rs
```diff
@@ -104,10 +104,23 @@ fn canonical_merkle_depth(tx_count: u128) -> u32 {
 /// `siblings` and `tx_index`, using Bitcoin's double-SHA-256 hashing.
 ///
 /// Validates the proof against the canonical tree shape implied by
-/// `tx_count`: rejects proofs whose path length doesn't match
-/// `ceil(log2(tx_count))`, and rejects `tx_index >= tx_count`. Together these
-/// prevent the CVE-2012-2459 ambiguity where an intermediate node `H(C, C)`
-/// in an odd-row-padded tree could pose as a leaf.
+/// `tx_count`. At every level the verifier tracks the real row size
+/// (`(row_count + 1) >> 1` per step up) and applies two consistency checks
+/// against each supplied sibling:
+///
+/// 1. If the sibling sits in the duplicated-padding slot of an odd row
+///    (`idx ^ 1 >= row_count`), it must equal the running hash — the only
+///    canonical value Bitcoin's "duplicate the last node" rule produces.
+/// 2. Otherwise the sibling must *not* equal the running hash. In a
+///    CVE-2012-2459-clean Bitcoin tree two adjacent subtrees can only share
+///    a hash if they share leaves, which the consensus rule forbids; a
+///    sibling that happens to equal `cur` at a non-padding position is
+///    therefore the fingerprint of an inflated-`tx_count` forgery that
+///    tries to relocate the last real leaf into the padded region (claiming
+///    e.g. `tx_count = 4` for a real 3-leaf tree).
+///
+/// Together with the `tx_index < tx_count` and path-length checks, these
+/// pin the proof to the canonical tree of a real Bitcoin block.
 fn verify_merkle(
     leaf: [u8; 32],
     root: [u8; 32],
@@ -125,9 +138,24 @@ fn verify_merkle(
 
     let mut cur = leaf;
     let mut idx = tx_index;
+    let mut row_count = tx_count;
     let mut buf = [0u8; 64];
 
     for sibling in siblings {
+        let sibling_idx = idx | 1;
+        if sibling_idx >= row_count {
+            // Canonical duplicated-padding slot: only valid when we are at
+            // the last position of an odd-sized row and the sibling is the
+            // duplicate of `cur` itself.
+            if row_count & 1 == 0 || idx != row_count - 1 || sibling != &cur {
+                return false;
+            }
+        } else if sibling == &cur {
+            // Non-padding position: a sibling equal to `cur` would require
+            // duplicate leaves below, which is invalid.
+            return false;
+        }
+
         if idx & 1 == 1 {
             buf[..32].copy_from_slice(sibling);
             buf[32..].copy_from_slice(&cur);
@@ -137,6 +165,7 @@ fn verify_merkle(
         }
         cur = Sha256dHash::from_data(&buf).0;
         idx >>= 1;
+        row_count = (row_count + 1) >> 1;
     }
 
     cur == root
@@ -174,9 +203,12 @@ pub fn cost_input_verify_merkle_proof(args: &[Value]) -> Result<u64, VmExecution
 /// (wrong types, wrong arity) propagate as runtime errors.
 ///
 /// `tx-count` is the total number of transactions in the block whose merkle
-/// root is being checked. It pins down the canonical tree shape and prevents
-/// CVE-2012-2459-style attacks where an intermediate node could be passed
-/// off as a leaf.
+/// root is being checked. It pins down the canonical tree shape: the
+/// verifier tracks the real row size at every level and rejects proofs
+/// whose path does not match a real Bitcoin block, including the
+/// CVE-2012-2459 "intermediate node posing as a leaf" and the
+/// inflated-`tx-count` variant where the last real leaf of an odd-sized
+/// tree is relocated into the duplicated-padding region.
 pub fn native_verify_merkle_proof(args: Vec<Value>) -> Result<Value, VmExecutionError> {
     let [
         leaf_value,
@@ -494,6 +526,65 @@ mod tests {
         // Forgery 2: claim a leaf at the duplicated-slot index 3. With
         // tx_count=3 we reject any index >= 3.
         assert!(!verify_merkle(c, root, 3, 3, &[c, h_ab]));
+
+        // Forgery 3: inflate tx_count to 4 to claim C is at index 3 of an
+        // even-sized tree. canonical_merkle_depth(4) == 2, so the path-length
+        // check still passes; what catches the forgery is the per-level
+        // tree-shape consistency check (the supplied sibling at the leaf
+        // level would equal `cur`, which a real Bitcoin block — clean of
+        // CVE-2012-2459 duplicate-txid forgeries — never produces at a
+        // non-padding position).
+        assert!(!verify_merkle(c, root, 3, 4, &[c, h_ab]));
+    }
+
+    #[test]
+    fn merkle_rejects_inflated_tx_count_deep_relocation() {
+        // 5-leaf tree, padded canonically as:
+        //   row 0: [A, B, C, D, E, E]
+        //   row 1: [H(A,B), H(C,D), H(E,E), H(E,E)]
+        //   row 2: [H1, H2]
+        //   row 3: Root
+        // The last real leaf E sits at index 4 with siblings [E, H(E,E), H1].
+        // The same siblings re-verify against the same root for every index
+        // in {5, 6, 7} if tx_count is inflated to 6, 7, or 8 — exactly the
+        // CVE-2012-2459 relocation window that this test pins shut.
+        let a = [0x01u8; 32];
+        let b = [0x02u8; 32];
+        let c = [0x03u8; 32];
+        let d = [0x04u8; 32];
+        let e = [0x05u8; 32];
+        let mut buf = [0u8; 64];
+
+        let mut h = |l: &[u8; 32], r: &[u8; 32]| {
+            buf[..32].copy_from_slice(l);
+            buf[32..].copy_from_slice(r);
+            Sha256dHash::from_data(&buf).0
+        };
+
+        let h_ab = h(&a, &b);
+        let h_cd = h(&c, &d);
+        let h_ee = h(&e, &e);
+        let h1 = h(&h_ab, &h_cd);
+        let h2 = h(&h_ee, &h_ee);
+        let root = h(&h1, &h2);
+
+        // Real proof for E at index 4 with tx_count=5 verifies.
+        assert!(verify_merkle(e, root, 4, 5, &[e, h_ee, h1]));
+
+        // Every relocation forgery is rejected.
+        for (idx, tx_count) in [(5u128, 6u128), (5, 8), (6, 7), (6, 8), (7, 8)] {
+            assert!(
+                !verify_merkle(e, root, idx, tx_count, &[e, h_ee, h1]),
+                "forgery (idx={idx}, tx_count={tx_count}) must be rejected",
+            );
+        }
+
+        // Sanity: also reject staying at the real index 4 but with an
+        // inflated tx_count=8 (forces a depth-3 path against an even tree).
+        // The forgery must still rebuild the same root, so the leaf-level
+        // sibling has to be E itself — caught by the non-padding equality
+        // check.
+        assert!(!verify_merkle(e, root, 4, 8, &[e, h_ee, h1]));
     }
 
     #[test]
@@ -823,35 +914,48 @@ mod tests {
     use stacks_common::deps_common::bitcoin::blockdata::transaction::{OutPoint, TxIn, TxOut};
     use stacks_common::deps_common::bitcoin::network::serialize::serialize as btc_serialize;
 
-    /// Walk a Bitcoin-style merkle proof bottom-up and return the root it
-    /// implies for `(leaf, tx_index)`. Used to synthesize valid proofs at
-    /// arbitrary depth without materializing 2^24-leaf trees in memory.
-    /// Independent canonical-tree coverage comes from the real-mainnet
-    /// merkle proof unit tests above.
-    fn compute_root_from_proof(leaf: [u8; 32], tx_index: u128, siblings: &[[u8; 32]]) -> [u8; 32] {
+    /// Walk a Bitcoin-style merkle proof bottom-up using the canonical tree
+    /// shape implied by `tx_count`, forcing the duplicated-padding sibling
+    /// at every odd-row edge to equal the running hash. Returns the synthesized
+    /// `(siblings, root)` pair. Used by the prop-test strategies to produce
+    /// proofs that are valid by construction for `verify_merkle`, without
+    /// materializing 2^24-leaf trees in memory. Independent canonical-tree
+    /// coverage comes from the real-mainnet merkle proof unit tests above.
+    fn synth_canonical_proof(
+        leaf: [u8; 32],
+        tx_index: u128,
+        tx_count: u128,
+        raw_siblings: &[[u8; 32]],
+    ) -> (Vec<[u8; 32]>, [u8; 32]) {
+        let mut siblings = Vec::with_capacity(raw_siblings.len());
         let mut cur = leaf;
         let mut idx = tx_index;
+        let mut row_count = tx_count;
         let mut buf = [0u8; 64];
-        for sibling in siblings {
+        for raw in raw_siblings {
+            let sibling = if (idx | 1) >= row_count { cur } else { *raw };
+            siblings.push(sibling);
             if idx & 1 == 1 {
-                buf[..32].copy_from_slice(sibling);
+                buf[..32].copy_from_slice(&sibling);
                 buf[32..].copy_from_slice(&cur);
             } else {
                 buf[..32].copy_from_slice(&cur);
-                buf[32..].copy_from_slice(sibling);
+                buf[32..].copy_from_slice(&sibling);
             }
             cur = Sha256dHash::from_data(&buf).0;
             idx >>= 1;
+            row_count = (row_count + 1) >> 1;
         }
-        cur
+        (siblings, cur)
     }
 
     prop_compose! {
         /// Synthesize a valid merkle proof spanning the full supported range:
         /// `tx_count` ranges over `1..=2^24` (depths 0..=24, the cap enforced
         /// by `VERIFY_MERKLE_PROOF_MAX_DEPTH`). Returns
-        /// `(leaf, root, tx_index, tx_count, siblings)` where `root` is
-        /// computed from the synthesized siblings, so the proof verifies by
+        /// `(leaf, root, tx_index, tx_count, siblings)` where `siblings`
+        /// matches the canonical Bitcoin tree shape for `(tx_index, tx_count)`
+        /// and `root` is the synthesized root, so the proof verifies by
         /// construction.
         fn arb_merkle_proof()(
             tx_count in 1u128..=(1u128 << VERIFY_MERKLE_PROOF_MAX_DEPTH),
@@ -860,12 +964,12 @@ mod tests {
             tx_index in 0u128..tx_count,
             leaf in Just(leaf),
             tx_count in Just(tx_count),
-            siblings in prop::collection::vec(
+            raw_siblings in prop::collection::vec(
                 any::<[u8; 32]>(),
                 canonical_merkle_depth(tx_count) as usize,
             ),
         ) -> ([u8; 32], [u8; 32], u128, u128, Vec<[u8; 32]>) {
-            let root = compute_root_from_proof(leaf, tx_index, &siblings);
+            let (siblings, root) = synth_canonical_proof(leaf, tx_index, tx_count, &raw_siblings);
             (leaf, root, tx_index, tx_count, siblings)
         }
     }
```

### clarity/src/vm/tests/bitcoin.rs
```diff
@@ -64,27 +64,39 @@ fn execute(snippet: &str) -> Value {
         .expect("should return a value")
 }
 
-/// Walk a Bitcoin-style merkle proof bottom-up and return the root it
-/// implies. Lets us synthesize valid proofs at the full 0..=24 depth range
-/// without materializing 2^24-leaf trees in memory. The canonical
-/// tree-construction direction is covered independently by the real-mainnet
-/// unit tests in `vm::functions::bitcoin::tests`.
-fn compute_root_from_proof(leaf: [u8; 32], tx_index: u128, siblings: &[[u8; 32]]) -> [u8; 32] {
+/// Walk a Bitcoin-style merkle proof bottom-up using the canonical tree
+/// shape implied by `tx_count`, forcing the duplicated-padding sibling at
+/// every odd-row edge to equal the running hash. Returns the synthesized
+/// `(siblings, root)` pair. Lets us synthesize valid proofs at the full
+/// 0..=24 depth range without materializing 2^24-leaf trees in memory.
+/// The canonical tree-construction direction is covered independently by
+/// the real-mainnet unit tests in `vm::functions::bitcoin::tests`.
+fn synth_canonical_proof(
+    leaf: [u8; 32],
+    tx_index: u128,
+    tx_count: u128,
+    raw_siblings: &[[u8; 32]],
+) -> (Vec<[u8; 32]>, [u8; 32]) {
+    let mut siblings = Vec::with_capacity(raw_siblings.len());
     let mut cur = leaf;
     let mut idx = tx_index;
+    let mut row_count = tx_count;
     let mut buf = [0u8; 64];
-    for sibling in siblings {
+    for raw in raw_siblings {
+        let sibling = if (idx | 1) >= row_count { cur } else { *raw };
+        siblings.push(sibling);
         if idx & 1 == 1 {
-            buf[..32].copy_from_slice(sibling);
+            buf[..32].copy_from_slice(&sibling);
             buf[32..].copy_from_slice(&cur);
         } else {
             buf[..32].copy_from_slice(&cur);
-            buf[32..].copy_from_slice(sibling);
+            buf[32..].copy_from_slice(&sibling);
         }
         cur = Sha256dHash::from_data(&buf).0;
         idx >>= 1;
+        row_count = (row_count + 1) >> 1;
     }
-    cur
+    (siblings, cur)
 }
 
 /// `ceil(log2(n))` for `n >= 2`, or 0 for `n <= 1` — local copy of the
@@ -101,21 +113,22 @@ prop_compose! {
     /// Synthesize a valid merkle proof spanning the full supported range:
     /// `tx_count` ranges over `1..=2^24` (depths 0..=24, the cap enforced by
     /// the `(list 24 (buff 32))` sibling type). Returns
-    /// `(leaf, root, tx_index, tx_count, siblings)` where `root` is computed
-    /// from the synthesized siblings, so the proof verifies by construction.
+    /// `(leaf, root, tx_index, tx_count, siblings)` where `siblings` matches
+    /// the canonical Bitcoin tree shape for `(tx_index, tx_count)` and `root`
+    /// is the synthesized root, so the proof verifies by construction.
     fn arb_merkle_proof()(
         tx_count in 1u128..=(1u128 << VERIFY_MERKLE_PROOF_MAX_DEPTH),
         leaf in any::<[u8; 32]>(),
     )(
         tx_index in 0u128..tx_count,
         leaf in Just(leaf),
         tx_count in Just(tx_count),
-        siblings in prop::collection::vec(
+        raw_siblings in prop::collection::vec(
             any::<[u8; 32]>(),
             canonical_merkle_depth(tx_count) as usize,
         ),
     ) -> ([u8; 32], [u8; 32], u128, u128, Vec<[u8; 32]>) {
-        let root = compute_root_from_proof(leaf, tx_index, &siblings);
+        let (siblings, root) = synth_canonical_proof(leaf, tx_index, tx_count, &raw_siblings);
         (leaf, root, tx_index, tx_count, siblings)
     }
 }
```
