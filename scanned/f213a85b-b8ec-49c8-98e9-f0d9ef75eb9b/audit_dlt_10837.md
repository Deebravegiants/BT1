# [?] fix: require tx-count in verify-merkle-proof (CVE-2012-2459)

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-05-03
Source: https://github.com/stacks-network/stacks-core/commit/aba677a9ad13acf3e959a180abc798c9636dabcc
Type: security-commit

## Details
fix: require tx-count in verify-merkle-proof (CVE-2012-2459)

Also check script pubkey length to ensure it doesn't exceed 1024.

## Patch
### clarity/src/vm/analysis/type_checker/v2_1/natives/mod.rs
```diff
@@ -879,7 +879,7 @@ fn check_verify_merkle_proof(
     args: &[SymbolicExpression],
     context: &TypingContext,
 ) -> Result<TypeSignature, StaticCheckError> {
-    check_argument_count(4, args)?;
+    check_argument_count(5, args)?;
     checker.type_check_expects(
         get_nth_argument(0, args)?,
         context,
@@ -895,14 +895,19 @@ fn check_verify_merkle_proof(
         context,
         &TypeSignature::UIntType,
     )?;
+    checker.type_check_expects(
+        get_nth_argument(3, args)?,
+        context,
+        &TypeSignature::UIntType,
+    )?;
     let siblings_type = TypeSignature::list_of(
         TypeSignature::BUFFER_32,
         VERIFY_MERKLE_PROOF_MAX_DEPTH,
     )
     .map_err(|_| {
         StaticCheckErrorKind::Unreachable("FATAL: failed to build (list 24 (buff 32)) type".into())
     })?;
-    checker.type_check_expects(get_nth_argument(3, args)?, context, &siblings_type)?;
+    checker.type_check_expects(get_nth_argument(4, args)?, context, &siblings_type)?;
     Ok(TypeSignature::BoolType)
 }
 
```

### clarity/src/vm/docs/mod.rs
```diff
@@ -1419,23 +1419,29 @@ NIST P-256 curve (also known as secp256r1).",
 };
 
 const VERIFY_MERKLE_PROOF_API: SpecialAPI = SpecialAPI {
-    input_type: "(buff 32), (buff 32), uint, (list 24 (buff 32))",
-    snippet: "verify-merkle-proof ${1:leaf-hash} ${2:root-hash} ${3:tx-index} ${4:sibling-hashes}",
+    input_type: "(buff 32), (buff 32), uint, uint, (list 24 (buff 32))",
+    snippet: "verify-merkle-proof ${1:leaf-hash} ${2:root-hash} ${3:tx-index} ${4:tx-count} ${5:sibling-hashes}",
     output_type: "bool",
-    signature: "(verify-merkle-proof leaf-hash root-hash tx-index sibling-hashes)",
+    signature: "(verify-merkle-proof leaf-hash root-hash tx-index tx-count sibling-hashes)",
     description:
         "The `verify-merkle-proof` function verifies a Bitcoin-style merkle inclusion proof
 using double-SHA-256 hashing with the \"duplicate the last node on odd-sized rows\" rule.
 
 Given a `leaf-hash` (typically a Bitcoin txid), the merkle `root-hash` of a block, the
-`tx-index` of the leaf within the tree (0-indexed), and the list of `sibling-hashes` along the
-path from the leaf to the root, the function returns `true` iff hashing pairwise up the tree
-in the order described by `tx-index` produces `root-hash`.
+`tx-index` of the leaf within the tree (0-indexed), the `tx-count` of transactions in the
+block, and the list of `sibling-hashes` along the path from the leaf to the root, the
+function returns `true` iff hashing pairwise up the tree in the order described by
+`tx-index` produces `root-hash`.
 
-All 32-byte hashes (leaf, root, siblings) are passed in *internal* (raw) byte order, not the
-display (reversed) order conventionally used for Bitcoin txids and block hashes. The `txid`
-returned by `get-bitcoin-tx-output?` is already in internal byte order and can be passed
-directly as `leaf-hash`.
+`tx-count` pins down the canonical Bitcoin tree shape and is required to defend against
+CVE-2012-2459-style attacks where an intermediate node in an odd-row-padded tree could
+otherwise be passed off as a leaf. The function rejects any proof whose path length doesn't
+match `ceil(log2(tx-count))` and any `tx-index` not less than `tx-count`.
+
+All 32-byte hashes (leaf, root, siblings) are passed in *internal* (raw) byte order, not
+the display (reversed) order conventionally used for Bitcoin txids and block hashes. The
+`txid` returned by `get-bitcoin-tx-output?` is already in internal byte order and can be
+passed directly as `leaf-hash`.
 
 Returns `false` for any malformed proof and `true` for a valid proof.",
     example: "
@@ -1446,6 +1452,7 @@ Returns `false` for any malformed proof and `true` for a valid proof.",
     0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
     0x3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a
     u0
+    u1
     (list)) ;; Returns true",
 };
 
```

### clarity/src/vm/functions/bitcoin.rs
```diff
@@ -42,6 +42,9 @@ use crate::vm::representations::SymbolicExpression;
 use crate::vm::types::{BuffData, ListData, SequenceData, TupleData, TypeSignature, Value};
 use crate::vm::{LocalContext, eval};
 
+/// Maximum supported merkle proof depth for `(verify-merkle-proof ...)`.
+const VERIFY_MERKLE_PROOF_MAX_DEPTH: u32 = 24;
+
 /// Parse a Bitcoin transaction (SegWit or non-SegWit) and pluck the output at
 /// `vout`, along with the canonical (non-witness) txid in internal byte order.
 ///
@@ -51,22 +54,57 @@ fn parse_tx_output(raw: &[u8], vout: u64) -> Option<(Vec<u8>, u64, [u8; 32])> {
     let tx: Transaction = btc_deserialize(raw).ok()?;
     let vout_idx = usize::try_from(vout).ok()?;
     let txout = tx.output.get(vout_idx)?;
-    let script = txout.script_pubkey.as_bytes().to_vec();
+    let script_bytes = txout.script_pubkey.as_bytes();
+    if script_bytes.len() > 1024 {
+        return None;
+    }
+    let script = script_bytes.to_vec();
     let amount = txout.value;
     let txid = tx.txid().0;
     Some((script, amount, txid))
 }
 
+/// Canonical Bitcoin merkle-tree depth for a block containing `tx_count`
+/// transactions. Returns `0` for an empty or single-tx tree (the leaf is the
+/// root); otherwise `ceil(log2(tx_count))`.
+fn canonical_merkle_depth(tx_count: u128) -> u32 {
+    if tx_count <= 1 {
+        0
+    } else {
+        // ceil(log2(n)) for n >= 2 == floor(log2(n - 1)) + 1
+        (tx_count - 1).ilog2() + 1
+    }
+}
+
 /// Verify that `leaf` reaches `root` along the merkle path described by
 /// `siblings` and `tx_index`, using Bitcoin's double-SHA-256 hashing.
-fn verify_merkle(leaf: [u8; 32], root: [u8; 32], tx_index: u128, siblings: &[[u8; 32]]) -> bool {
+///
+/// Validates the proof against the canonical tree shape implied by
+/// `tx_count`: rejects proofs whose path length doesn't match
+/// `ceil(log2(tx_count))`, and rejects `tx_index >= tx_count`. Together these
+/// prevent the CVE-2012-2459 ambiguity where an intermediate node `H(C, C)`
+/// in an odd-row-padded tree could pose as a leaf.
+fn verify_merkle(
+    leaf: [u8; 32],
+    root: [u8; 32],
+    tx_index: u128,
+    tx_count: u128,
+    siblings: &[[u8; 32]],
+) -> bool {
+    if tx_count == 0 || tx_index >= tx_count {
+        return false;
+    }
+    let expected_depth = canonical_merkle_depth(tx_count);
+    if siblings.len() as u64 != u64::from(expected_depth) {
+        return false;
+    }
+
     let mut cur = leaf;
     let mut idx = tx_index;
     let mut buf = [0u8; 64];
 
     for sibling in siblings {
         if idx & 1 == 1 {
-            // current node is the right child, sibling is on the left
             buf[..32].copy_from_slice(sibling);
             buf[32..].copy_from_slice(&cur);
         } else {
@@ -94,17 +132,22 @@ fn buff_to_array_32(value: &Value) -> Option<[u8; 32]> {
 
 /// Implements the `verify-merkle-proof` Clarity 6 builtin.
 ///
-/// `(verify-merkle-proof leaf-hash root-hash tx-index sibling-hashes)`
+/// `(verify-merkle-proof leaf-hash root-hash tx-index tx-count sibling-hashes)`
 /// returns `bool`. Hashes are expected in internal byte order. Returns
 /// `false` for any structurally invalid proof; only argument-shape errors
 /// (wrong types, wrong arity) propagate as runtime errors.
+///
+/// `tx-count` is the total number of transactions in the block whose merkle
+/// root is being checked. It pins down the canonical tree shape and prevents
+/// CVE-2012-2459-style attacks where an intermediate node could be passed
+/// off as a leaf.
 pub fn special_verify_merkle_proof(
     args: &[SymbolicExpression],
     exec_state: &mut ExecutionState,
     invoke_ctx: &InvocationContext,
     context: &LocalContext,
 ) -> Result<Value, VmExecutionError> {
-    check_argument_count(4, args)?;
+    check_argument_count(5, args)?;
 
     let leaf_value = eval(&args[0], exec_state, invoke_ctx, context)?;
     let leaf = match buff_to_array_32(leaf_value.as_ref()) {
@@ -142,12 +185,32 @@ pub fn special_verify_merkle_proof(
         }
     };
 
-    let siblings_value = eval(&args[3], exec_state, invoke_ctx, context)?;
+    let tx_count_value = eval(&args[3], exec_state, invoke_ctx, context)?;
+    let tx_count = match tx_count_value.as_ref() {
+        Value::UInt(v) => *v,
+        _ => {
+            return Err(RuntimeCheckErrorKind::TypeValueError(
+                Box::new(TypeSignature::UIntType),
+                tx_count_value.as_ref().to_error_string(),
+            )
+            .into());
+        }
+    };
+
+    let siblings_value = eval(&args[4], exec_state, invoke_ctx, context)?;
     let siblings_data = match siblings_value.as_ref() {
         Value::Sequence(SequenceData::List(ListData { data, .. })) => data.clone(),
         _ => {
-            return Err(RuntimeCheckErrorKind::Unreachable(
-                "verify-merkle-proof expected a list of (buff 32)".into(),
+            let expected =
+                TypeSignature::list_of(TypeSignature::BUFFER_32, VERIFY_MERKLE_PROOF_MAX_DEPTH)
+                    .map_err(|_| {
+                        VmInternalError::Expect(
+                            "FATAL: failed to build (list 24 (buff 32)) type".into(),
+                        )
+                    })?;
+            return Err(RuntimeCheckErrorKind::TypeValueError(
+                Box::new(expected),
+                siblings_value.as_ref().to_error_string(),
             )
             .into());
         }
@@ -170,7 +233,9 @@ pub fn special_verify_merkle_proof(
         }
     }
 
-    Ok(Value::Bool(verify_merkle(leaf, root, tx_index, &siblings)))
+    Ok(Value::Bool(verify_merkle(
+        leaf, root, tx_index, tx_count, &siblings,
+    )))
 }
 
 /// Implements the `get-bitcoin-tx-output?` Clarity 6 builtin.
@@ -316,7 +381,7 @@ mod tests {
         // With one tx the txid IS the merkle root; an empty proof should verify
         // trivially.
         let leaf = [0x42u8; 32];
-        assert!(verify_merkle(leaf, leaf, 0, &[]));
+        assert!(verify_merkle(leaf, leaf, 0, 1, &[]));
     }
 
     #[test]
@@ -329,11 +394,72 @@ mod tests {
         let root = Sha256dHash::from_data(&buf).0;
 
         // Left leaf: tx_index 0, sibling is the right leaf.
-        assert!(verify_merkle(l, root, 0, &[r]));
+        assert!(verify_merkle(l, root, 0, 2, &[r]));
         // Right leaf: tx_index 1, sibling is the left leaf.
-        assert!(verify_merkle(r, root, 1, &[l]));
+        assert!(verify_merkle(r, root, 1, 2, &[l]));
         // Wrong index → fails.
-        assert!(!verify_merkle(l, root, 1, &[r]));
+        assert!(!verify_merkle(l, root, 1, 2, &[r]));
+    }
+
+    #[test]
+    fn merkle_rejects_oversized_tx_index() {
+        let l = [0x11u8; 32];
+        let r = [0x22u8; 32];
+        let mut buf = [0u8; 64];
+        buf[..32].copy_from_slice(&l);
+        buf[32..].copy_from_slice(&r);
+        let root = Sha256dHash::from_data(&buf).0;
+
+        assert!(verify_merkle(l, root, 0, 2, &[r]));
+        // tx_index >= tx_count must be rejected.
+        assert!(!verify_merkle(l, root, 2, 2, &[r]));
+        assert!(!verify_merkle(l, root, u128::MAX, 2, &[r]));
+    }
+
+    #[test]
+    fn merkle_rejects_cve_2012_2459_intermediate_node() {
+        // Build a 3-leaf tree, which Bitcoin pads as [A, B, C, C].
+        let a = [0x01u8; 32];
+        let b = [0x02u8; 32];
+        let c = [0x03u8; 32];
+        let mut buf = [0u8; 64];
+
+        buf[..32].copy_from_slice(&a);
+        buf[32..].copy_from_slice(&b);
+        let h_ab = Sha256dHash::from_data(&buf).0;
+
+        buf[..32].copy_from_slice(&c);
+        buf[32..].copy_from_slice(&c);
+        let h_cc = Sha256dHash::from_data(&buf).0;
+
+        buf[..32].copy_from_slice(&h_ab);
+        buf[32..].copy_from_slice(&h_cc);
+        let root = Sha256dHash::from_data(&buf).0;
+
+        // Real leaf C at index 2 (canonical depth is 2; siblings are [C, h_ab]).
+        assert!(verify_merkle(c, root, 2, 3, &[c, h_ab]));
+
+        // Forgery 1: claim h_cc (an intermediate node) is a leaf at index 1
+        // with depth-1 proof. With tx_count=3 we expect depth 2, so reject.
+        assert!(!verify_merkle(h_cc, root, 1, 3, &[h_ab]));
+
+        // Forgery 2: claim a leaf at the duplicated-slot index 3. With
+        // tx_count=3 we reject any index >= 3.
+        assert!(!verify_merkle(c, root, 3, 3, &[c, h_ab]));
+    }
+
+    #[test]
+    fn canonical_depth_table() {
+        assert_eq!(canonical_merkle_depth(0), 0);
+        assert_eq!(canonical_merkle_depth(1), 0);
+        assert_eq!(canonical_merkle_depth(2), 1);
+        assert_eq!(canonical_merkle_depth(3), 2);
+        assert_eq!(canonical_merkle_depth(4), 2);
+        assert_eq!(canonical_merkle_depth(5), 3);
+        assert_eq!(canonical_merkle_depth(8), 3);
+        assert_eq!(canonical_merkle_depth(9), 4);
+        assert_eq!(canonical_merkle_depth(16), 4);
+        assert_eq!(canonical_merkle_depth(17), 5);
     }
 
     #[test]
```

### stackslib/src/clarity_vm/tests/costs.rs
```diff
@@ -188,7 +188,7 @@ pub fn get_simple_test(function: &NativeFunctions) -> Option<&'static str> {
         RestrictAssets => "(restrict-assets? tx-sender () (+ u1 u2))",
         AsContractSafe => "(as-contract? () (+ u1 u2))",
         Secp256r1Verify => "(secp256r1-verify 0xc3abef6a775793dfbc8e0719e7a1de1fc2f90d37a7912b1ce8e300a5a03b06a8 0xf2b8c0645caa7250e3b96d633cf40a88456e4ffbddffb69200c4e019039dfd310eac59293c23e6d6aa8b0c5d9e4e48fa4c4fdf1ace2ba618dc0263b5e90a0903 0x031e18532fd4754c02f3041d9c75ceb33b83ffd81ac7ce4fe882ccb1c98bc5896e)",
-        VerifyMerkleProof => "(verify-merkle-proof 0x0000000000000000000000000000000000000000000000000000000000000000 0x0000000000000000000000000000000000000000000000000000000000000000 u0 (list))",
+        VerifyMerkleProof => "(verify-merkle-proof 0x0000000000000000000000000000000000000000000000000000000000000000 0x0000000000000000000000000000000000000000000000000000000000000000 u0 u1 (list))",
         GetBitcoinTxOutput => "(get-bitcoin-tx-output? 0x0100000001000000000000000000000000000000000000000000000000000000000000000000000000ffffffff01e80300000000000016001400000000000000000000000000000000000000000000000000 u0)",
         // These expressions are not usable in this context, since they are
         // only allowed within `restrict-assets?` or `as-contract?`
```
