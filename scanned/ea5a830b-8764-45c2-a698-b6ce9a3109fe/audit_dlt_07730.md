# [?] fix(net): prevent eth/68 tx request packing overflow (#23848)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-04-30
Source: https://github.com/paradigmxyz/reth/commit/0eeb8c5ef7e6df23afd7ef2d413246d9131d754c
Type: security-commit

## Details
fix(net): prevent eth/68 tx request packing overflow (#23848)

## Patch
### crates/net/network/src/transactions/fetcher.rs
```diff
@@ -283,11 +283,12 @@ impl<N: NetworkPrimitives> TransactionFetcher<N> {
                 unreachable!("this method is called upon reception of an eth68 announcement")
             };
 
-            let next_acc_size = acc_size_response + size;
+            let next_acc_size = acc_size_response.checked_add(size).filter(|next_acc_size| {
+                *next_acc_size <=
+                    self.info.soft_limit_byte_size_pooled_transactions_response_on_pack_request
+            });
 
-            if next_acc_size <=
-                self.info.soft_limit_byte_size_pooled_transactions_response_on_pack_request
-            {
+            if let Some(next_acc_size) = next_acc_size {
                 // only update accumulated size of tx response if tx will fit in without exceeding
                 // soft limit
                 acc_size_response = next_acc_size;
@@ -721,7 +722,7 @@ impl<N: NetworkPrimitives> TransactionFetcher<N> {
                 .and_then(|entry| entry.tx_encoded_len())
                 .unwrap_or(AVERAGE_BYTE_SIZE_TX_ENCODED);
 
-            acc_size_response += size;
+            acc_size_response = acc_size_response.saturating_add(size);
 
             // 4. Check if acc size or hashes count is at limit, if so stop looping.
             // if expected response is full enough or the number of hashes in the request is
@@ -1368,6 +1369,43 @@ mod test {
         assert_eq!(expected_surplus_hashes, surplus_eth68_hashes);
     }
 
+    #[test]
+    fn pack_eth68_request_does_not_overflow_announced_size() {
+        reth_tracing::init_test_tracing();
+
+        let tx_fetcher = &mut TransactionFetcher::<EthNetworkPrimitives>::default();
+
+        let eth68_hashes =
+            [B256::from_slice(&[1; 32]), B256::from_slice(&[2; 32]), B256::from_slice(&[3; 32])];
+        let eth68_sizes = [
+            DEFAULT_SOFT_LIMIT_BYTE_SIZE_POOLED_TRANSACTIONS_RESP_ON_PACK_GET_POOLED_TRANSACTIONS_REQ - MEDIAN_BYTE_SIZE_SMALL_LEGACY_TX_ENCODED - 1,
+            usize::MAX,
+            2,
+        ];
+
+        let expected_request_hashes =
+            [eth68_hashes[0], eth68_hashes[2]].into_iter().collect::<HashSet<_>>();
+        let expected_surplus_hashes = std::iter::once(eth68_hashes[1]).collect::<HashSet<_>>();
+
+        let mut eth68_hashes_to_request = RequestTxHashes::with_capacity(3);
+        let valid_announcement_data = TestValidAnnouncementData(
+            eth68_hashes
+                .into_iter()
+                .zip(eth68_sizes)
+                .map(|(hash, size)| (hash, Some((0u8, size))))
+                .collect::<Vec<_>>(),
+        );
+
+        let surplus_eth68_hashes =
+            tx_fetcher.pack_request_eth68(&mut eth68_hashes_to_request, valid_announcement_data);
+
+        let eth68_hashes_to_request = eth68_hashes_to_request.into_iter().collect::<HashSet<_>>();
+        let surplus_eth68_hashes = surplus_eth68_hashes.into_iter().collect::<HashSet<_>>();
+
+        assert_eq!(expected_request_hashes, eth68_hashes_to_request);
+        assert_eq!(expected_surplus_hashes, surplus_eth68_hashes);
+    }
+
     #[tokio::test]
     async fn test_on_fetch_pending_hashes() {
         reth_tracing::init_test_tracing();
```
