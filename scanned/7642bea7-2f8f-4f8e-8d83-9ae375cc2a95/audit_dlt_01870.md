# [?] fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input (#19361)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-03-10
Source: https://github.com/ethereum-optimism/optimism/commit/37c98925e438efa476c6b598b5113b73dc6dbe76
Type: security-commit

## Details
fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input (#19361)

* fix(kona/protocol): add bounds checks in span batch decode to prevent panics on truncated input

Multiple span batch decode functions panic on truncated input instead of
returning an error. This adds explicit length checks before each unsafe
slice operation:

- prefix.rs: decode_parent_check and decode_l1_origin_check now check
  r.len() >= 20 before split_at(20)
- transactions.rs: decode_tx_sigs now checks r.len() >= 64 before
  indexing r[..32] and r[32..64]
- transactions.rs: decode_tx_tos now checks r.len() >= 20 before
  indexing r[..20]

On short input, each function returns SpanBatchError::Decoding(...)
instead of panicking, allowing the batch to be dropped gracefully —
consistent with Go op-node's io.ReadFull behavior.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix rustfmt formatting in span batch decode

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix clippy field_reassign_with_default in span batch tests

Use struct initialization syntax instead of Default::default()
followed by field reassignment.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style: fix rustfmt formatting for struct initialization

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### rust/kona/crates/protocol/protocol/src/batch/prefix.rs
```diff
@@ -47,6 +47,9 @@ impl SpanBatchPrefix {
 
     /// Decodes the parent check from a reader.
     pub fn decode_parent_check(&mut self, r: &mut &[u8]) -> Result<(), SpanBatchError> {
+        if r.len() < 20 {
+            return Err(SpanBatchError::Decoding(SpanDecodingError::ParentCheck));
+        }
         let (parent_check, remaining) = r.split_at(20);
         let parent_check = FixedBytes::<20>::from_slice(parent_check);
         *r = remaining;
@@ -56,6 +59,9 @@ impl SpanBatchPrefix {
 
     /// Decodes the L1 origin check from a reader.
     pub fn decode_l1_origin_check(&mut self, r: &mut &[u8]) -> Result<(), SpanBatchError> {
+        if r.len() < 20 {
+            return Err(SpanBatchError::Decoding(SpanDecodingError::L1OriginCheck));
+        }
         let (l1_origin_check, remaining) = r.split_at(20);
         let l1_origin_check = FixedBytes::<20>::from_slice(l1_origin_check);
         *r = remaining;
@@ -79,6 +85,29 @@ mod test {
     use alloc::vec::Vec;
     use alloy_primitives::address;
 
+    #[test]
+    fn test_decode_parent_check_truncated() {
+        let mut prefix = SpanBatchPrefix::default();
+        let buf = [0u8; 19]; // one byte short
+        let result = prefix.decode_parent_check(&mut buf.as_slice());
+        assert_eq!(result, Err(SpanBatchError::Decoding(SpanDecodingError::ParentCheck)));
+    }
+
+    #[test]
+    fn test_decode_l1_origin_check_truncated() {
+        let mut prefix = SpanBatchPrefix::default();
+        let buf = [0u8; 19]; // one byte short
+        let result = prefix.decode_l1_origin_check(&mut buf.as_slice());
+        assert_eq!(result, Err(SpanBatchError::Decoding(SpanDecodingError::L1OriginCheck)));
+    }
+
+    #[test]
+    fn test_decode_parent_check_empty() {
+        let mut prefix = SpanBatchPrefix::default();
+        let result = prefix.decode_parent_check(&mut [].as_slice());
+        assert_eq!(result, Err(SpanBatchError::Decoding(SpanDecodingError::ParentCheck)));
+    }
+
     #[test]
     fn test_span_batch_prefix_encoding_roundtrip() {
         let expected = SpanBatchPrefix {
```

### rust/kona/crates/protocol/protocol/src/batch/transactions.rs
```diff
@@ -153,6 +153,11 @@ impl SpanBatchTransactions {
         let mut sigs = Vec::with_capacity(self.total_block_tx_count as usize);
         for i in 0..self.total_block_tx_count {
             let y_parity = y_parity_bits.get_bit(i as usize).expect("same length");
+            if r.len() < 64 {
+                return Err(SpanBatchError::Decoding(
+                    SpanDecodingError::InvalidTransactionSignature,
+                ));
+            }
             let r_val = U256::from_be_slice(&r[..32]);
             let s_val = U256::from_be_slice(&r[32..64]);
             sigs.push(Signature::new(r_val, s_val, y_parity == 1));
@@ -193,6 +198,9 @@ impl SpanBatchTransactions {
         let mut tos = Vec::with_capacity(self.total_block_tx_count as usize);
         let contract_creation_count = self.contract_creation_count();
         for _ in 0..(self.total_block_tx_count - contract_creation_count) {
+            if r.len() < 20 {
+                return Err(SpanBatchError::Decoding(SpanDecodingError::InvalidTransactionData));
+            }
             let to = Address::from_slice(&r[..20]);
             tos.push(to);
             r.advance(20);
@@ -356,6 +364,48 @@ mod tests {
     use alloy_consensus::{Signed, TxEip1559, TxEip2930, TxEip7702};
     use alloy_primitives::{Signature, TxKind, address};
 
+    #[test]
+    fn test_decode_tx_sigs_truncated() {
+        let mut txs = SpanBatchTransactions { total_block_tx_count: 1, ..Default::default() };
+        // Provide a valid y_parity bitfield (1 bit = 1 byte) but truncated signature data
+        // SpanBatchBits::decode for 1 bit needs 1 byte for the bitfield
+        let buf = vec![0u8]; // y_parity byte, but no r/s signature bytes
+        let result = txs.decode_tx_sigs(&mut buf.as_slice());
+        assert_eq!(
+            result,
+            Err(SpanBatchError::Decoding(SpanDecodingError::InvalidTransactionSignature))
+        );
+    }
+
+    #[test]
+    fn test_decode_tx_tos_truncated() {
+        let mut txs = SpanBatchTransactions {
+            total_block_tx_count: 1,
+            contract_creation_bits: SpanBatchBits::default(),
+            ..Default::default()
+        };
+        let buf = [0u8; 19]; // one byte short of a 20-byte address
+        let result = txs.decode_tx_tos(&mut buf.as_slice());
+        assert_eq!(
+            result,
+            Err(SpanBatchError::Decoding(SpanDecodingError::InvalidTransactionData))
+        );
+    }
+
+    #[test]
+    fn test_decode_tx_tos_empty() {
+        let mut txs = SpanBatchTransactions {
+            total_block_tx_count: 1,
+            contract_creation_bits: SpanBatchBits::default(),
+            ..Default::default()
+        };
+        let result = txs.decode_tx_tos(&mut [].as_slice());
+        assert_eq!(
+            result,
+            Err(SpanBatchError::Decoding(SpanDecodingError::InvalidTransactionData))
+        );
+    }
+
     #[test]
     fn test_span_batch_transactions_add_empty_txs() {
         let mut span_batch_txs = SpanBatchTransactions::default();
```
