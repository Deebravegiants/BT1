# [?] Fix optional response crashes

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2023-12-21
Source: https://github.com/casper-network/casper-node/commit/2f4a199592565b292c8ddb5df686e8905aee51f7
Type: security-commit

## Details
Fix optional response crashes

## Patch
### node/src/components/binary_port.rs
```diff
@@ -422,9 +422,9 @@ where
 {
     match req {
         NonPersistedDataRequest::BlockHeight2Hash { height } => {
-            BinaryResponse::from_value(effect_builder.get_block_hash_for_height(height).await)
+            BinaryResponse::from_option(effect_builder.get_block_hash_for_height(height).await)
         }
-        NonPersistedDataRequest::HighestCompleteBlock => BinaryResponse::from_value(
+        NonPersistedDataRequest::HighestCompleteBlock => BinaryResponse::from_option(
             effect_builder
                 .get_highest_complete_block_header_from_storage()
                 .await
@@ -440,7 +440,7 @@ where
             )
         }
         NonPersistedDataRequest::TransactionHash2BlockHashAndHeight { transaction_hash } => {
-            BinaryResponse::from_value(
+            BinaryResponse::from_option(
                 effect_builder
                     .get_block_hash_and_height_for_transaction(transaction_hash)
                     .await,
@@ -473,10 +473,10 @@ where
                 .await,
         ),
         NonPersistedDataRequest::NextUpgrade => {
-            BinaryResponse::from_value(effect_builder.get_next_upgrade().await)
+            BinaryResponse::from_option(effect_builder.get_next_upgrade().await)
         }
         NonPersistedDataRequest::ConsensusStatus => {
-            BinaryResponse::from_value(effect_builder.consensus_status().await)
+            BinaryResponse::from_option(effect_builder.consensus_status().await)
         }
         NonPersistedDataRequest::ChainspecRawBytes => {
             BinaryResponse::from_value((*effect_builder.get_chainspec_raw_bytes().await).clone())
```

### types/src/binary_port/binary_response.rs
```diff
@@ -86,6 +86,18 @@ impl BinaryResponse {
         }
     }
 
+    /// Creates a new binary response from an optional value.
+    pub fn from_option<V>(opt: Option<V>) -> Self
+    where
+        V: ToBytes,
+        V: Into<PayloadType>,
+    {
+        match opt {
+            Some(val) => Self::from_value(val),
+            None => Self::new_empty(),
+        }
+    }
+
     /// Returns true if response is success.
     pub fn is_success(&self) -> bool {
         self.header.is_success()
```
