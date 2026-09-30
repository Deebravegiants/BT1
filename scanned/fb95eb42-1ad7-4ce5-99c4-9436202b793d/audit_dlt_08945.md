# [?] fix(core): avoid HyperlaneMessage::from panics in indexer paths (#9181)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2026-08-05
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/b79b5558865cc4e09ef2c499cb0656259e8c41b4
Type: security-commit

## Details
fix(core): avoid HyperlaneMessage::from panics in indexer paths (#9181)

## Patch
### rust/main/chains/hyperlane-cosmos/src/native/module_query_client.rs
```diff
@@ -17,7 +17,7 @@ use hyperlane_cosmos_rs::prost::{Message, Name};
 use tonic::async_trait;
 
 use hyperlane_core::{
-    ChainCommunicationError, ChainResult, HyperlaneMessage, RawHyperlaneMessage, H256, H512,
+    ChainCommunicationError, ChainResult, Decode, HyperlaneMessage, RawHyperlaneMessage, H256, H512,
 };
 
 use crate::GrpcProvider;
@@ -93,7 +93,7 @@ impl ModuleQueryClient {
                 let result = MsgProcessMessage::decode(msg.value.as_slice())
                     .map_err(HyperlaneCosmosError::from)?;
                 let message: RawHyperlaneMessage = hex::decode(result.message)?;
-                let message = HyperlaneMessage::from(message);
+                let message = HyperlaneMessage::read_from(&mut message.as_slice())?;
                 Ok(Some(message.recipient))
             }
             None => Ok(None),
```

### rust/main/chains/hyperlane-ethereum/src/contracts/mailbox.rs
```diff
@@ -21,9 +21,9 @@ use tracing::{instrument, warn};
 
 use hyperlane_core::{
     rpc_clients::call_and_retry_indefinitely, BatchItem, BatchResult, ChainCommunicationError,
-    ChainResult, ContractLocator, HyperlaneAbi, HyperlaneChain, HyperlaneContract, HyperlaneDomain,
-    HyperlaneMessage, HyperlaneProtocolError, HyperlaneProvider, Indexed, Indexer, LogMeta,
-    Mailbox, QueueOperation, RawHyperlaneMessage, ReorgPeriod, SequenceAwareIndexer,
+    ChainResult, ContractLocator, Decode, HyperlaneAbi, HyperlaneChain, HyperlaneContract,
+    HyperlaneDomain, HyperlaneMessage, HyperlaneProtocolError, HyperlaneProvider, Indexed, Indexer,
+    LogMeta, Mailbox, QueueOperation, RawHyperlaneMessage, ReorgPeriod, SequenceAwareIndexer,
     TxCostEstimate, TxOutcome, H160, H256, H512, U256,
 };
 
@@ -202,13 +202,13 @@ where
             .query_with_meta()
             .await?
             .into_iter()
-            .map(|(event, meta)| {
-                (
-                    HyperlaneMessage::from(event.message.to_vec()).into(),
+            .map(|(event, meta)| -> ChainResult<_> {
+                Ok((
+                    HyperlaneMessage::read_from(&mut event.message.as_ref())?.into(),
                     meta.into(),
-                )
+                ))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
 
         events.sort_by(|a, b| a.0.inner().nonce.cmp(&b.0.inner().nonce));
         Ok(events)
@@ -234,13 +234,13 @@ where
         .await;
         let logs = raw_logs_and_meta
             .into_iter()
-            .map(|(log, log_meta)| {
-                (
-                    HyperlaneMessage::from(log.message.to_vec()).into(),
+            .map(|(log, log_meta)| -> ChainResult<_> {
+                Ok((
+                    HyperlaneMessage::read_from(&mut log.message.as_ref())?.into(),
                     log_meta,
-                )
+                ))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
         Ok(logs)
     }
 
@@ -303,8 +303,13 @@ where
 
         let messages = raw_dispatch_logs
             .into_iter()
-            .map(|(log, meta)| (HyperlaneMessage::from(log.message.to_vec()).into(), meta))
-            .collect();
+            .map(|(log, meta)| -> ChainResult<_> {
+                Ok((
+                    HyperlaneMessage::read_from(&mut log.message.as_ref())?.into(),
+                    meta,
+                ))
+            })
+            .collect::<ChainResult<Vec<_>>>()?;
 
         Ok((messages, is_cctp_v2))
     }
```

### rust/main/chains/hyperlane-fuel/src/provider.rs
```diff
@@ -17,9 +17,9 @@ use fuels::{
 };
 use futures::future::join_all;
 use hyperlane_core::{
-    h512_to_bytes, BlockInfo, ChainCommunicationError, ChainInfo, ChainResult, HyperlaneChain,
-    HyperlaneDomain, HyperlaneMessage, HyperlaneProvider, HyperlaneProviderError, Indexed, LogMeta,
-    TxnInfo, H256, H512, U256,
+    h512_to_bytes, BlockInfo, ChainCommunicationError, ChainInfo, ChainResult, Decode,
+    HyperlaneChain, HyperlaneDomain, HyperlaneMessage, HyperlaneProvider, HyperlaneProviderError,
+    Indexed, LogMeta, TxnInfo, H256, H512, U256,
 };
 
 use crate::{make_client, make_provider, prelude::FuelIntoH256, ConnectionConf};
@@ -240,14 +240,17 @@ impl FuelProvider {
                     })
                     .next()?; // Each dispatch call should have only one log data receipt
 
-                if !receipt_log_data.is_empty() {
-                    // We cut out the message id, recipient and domain which are encoded in the first 76 bytes
-                    receipt_log_data.drain(0..76);
-                    let encoded_message = HyperlaneMessage::from(receipt_log_data);
-                    Some((tx_id, tx_data, encoded_message, log_index))
-                } else {
-                    None
+                // 76-byte Fuel prefix + ≥77-byte Hyperlane message; guard before drain/parse.
+                const FUEL_DISPATCH_PREFIX_LEN: usize = 76;
+                const HYPERLANE_MESSAGE_PREFIX_LEN: usize = 77;
+                if receipt_log_data.len() < FUEL_DISPATCH_PREFIX_LEN + HYPERLANE_MESSAGE_PREFIX_LEN
+                {
+                    return None;
                 }
+                receipt_log_data.drain(0..FUEL_DISPATCH_PREFIX_LEN);
+                let encoded_message =
+                    HyperlaneMessage::read_from(&mut receipt_log_data.as_slice()).ok()?;
+                Some((tx_id, tx_data, encoded_message, log_index))
             })
             .collect::<Vec<(Bytes32, TransactionResponse, HyperlaneMessage, U256)>>(); // Collect all Vec<u8> from each transaction into a Vec<Vec<u8>>
 
```

### rust/main/chains/hyperlane-radix/src/indexer/dispatch.rs
```diff
@@ -3,7 +3,7 @@ use std::ops::RangeInclusive;
 use async_trait::async_trait;
 
 use hyperlane_core::{
-    ChainResult, ContractLocator, HyperlaneMessage, Indexed, Indexer, LogMeta,
+    ChainResult, ContractLocator, Decode, HyperlaneMessage, Indexed, Indexer, LogMeta,
     SequenceAwareIndexer, H512,
 };
 
@@ -28,6 +28,10 @@ impl RadixDispatchIndexer {
     }
 }
 
+fn decode_dispatch_message(message: &[u8]) -> ChainResult<HyperlaneMessage> {
+    Ok(HyperlaneMessage::read_from(&mut &message[..])?)
+}
+
 #[async_trait]
 impl Indexer<HyperlaneMessage> for RadixDispatchIndexer {
     #[allow(clippy::blocks_in_conditions)] // TODO: `rustc` 1.80.1 clippy issue
@@ -41,12 +45,12 @@ impl Indexer<HyperlaneMessage> for RadixDispatchIndexer {
             .await?;
         let result = events
             .into_iter()
-            .map(|(event, meta)| {
-                let message: HyperlaneMessage = event.message.into();
+            .map(|(event, meta)| -> ChainResult<_> {
+                let message = decode_dispatch_message(&event.message)?;
                 let sequence = event.sequence;
-                (Indexed::new(message).with_sequence(sequence), meta)
+                Ok((Indexed::new(message).with_sequence(sequence), meta))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
         Ok(result)
     }
 
@@ -64,12 +68,12 @@ impl Indexer<HyperlaneMessage> for RadixDispatchIndexer {
             .await?;
         let result = events
             .into_iter()
-            .map(|(event, meta)| {
-                let message: HyperlaneMessage = event.message.into();
+            .map(|(event, meta)| -> ChainResult<_> {
+                let message = decode_dispatch_message(&event.message)?;
                 let sequence = event.sequence;
-                (Indexed::new(message).with_sequence(sequence), meta)
+                Ok((Indexed::new(message).with_sequence(sequence), meta))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
         Ok(result)
     }
 }
@@ -84,3 +88,36 @@ impl SequenceAwareIndexer<HyperlaneMessage> for RadixDispatchIndexer {
         Ok((Some(sequence), state_version.try_into()?))
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::decode_dispatch_message;
+    use hyperlane_core::{Decode, HyperlaneMessage, RawHyperlaneMessage, H256};
+
+    #[test]
+    fn decode_dispatch_message_rejects_malformed_short_bytes() {
+        assert!(decode_dispatch_message(&[]).is_err());
+        assert!(decode_dispatch_message(&[0u8; 40]).is_err());
+        assert!(decode_dispatch_message(&[0u8; 76]).is_err());
+    }
+
+    #[test]
+    fn decode_dispatch_message_accepts_valid_bytes() {
+        let expected = HyperlaneMessage {
+            version: 3,
+            nonce: 7,
+            origin: 1,
+            sender: H256::repeat_byte(0x11),
+            destination: 2,
+            recipient: H256::repeat_byte(0x22),
+            body: b"radix".to_vec(),
+        };
+        let bytes = RawHyperlaneMessage::from(&expected);
+        let decoded = decode_dispatch_message(&bytes).expect("valid dispatch message");
+        assert_eq!(decoded, expected);
+        assert_eq!(
+            HyperlaneMessage::read_from(&mut bytes.as_slice()).unwrap(),
+            decoded
+        );
+    }
+}
```

### rust/main/chains/hyperlane-tron/src/contracts/mailbox.rs
```diff
@@ -11,7 +11,7 @@ use hyperlane_core::Metadata;
 use tracing::instrument;
 
 use hyperlane_core::{
-    rpc_clients::call_and_retry_indefinitely, ChainResult, ContractLocator, HyperlaneChain,
+    rpc_clients::call_and_retry_indefinitely, ChainResult, ContractLocator, Decode, HyperlaneChain,
     HyperlaneContract, HyperlaneDomain, HyperlaneMessage, HyperlaneProvider, Indexed, Indexer,
     LogMeta, Mailbox, RawHyperlaneMessage, ReorgPeriod, SequenceAwareIndexer, TxCostEstimate,
     TxOutcome, H256, H512, U256,
@@ -60,13 +60,13 @@ impl Indexer<HyperlaneMessage> for TronMailboxIndexer {
             .query_with_meta()
             .await?
             .into_iter()
-            .map(|(event, meta)| {
-                (
-                    HyperlaneMessage::from(event.message.to_vec()).into(),
+            .map(|(event, meta)| -> ChainResult<_> {
+                Ok((
+                    HyperlaneMessage::read_from(&mut event.message.as_ref())?.into(),
                     meta.into(),
-                )
+                ))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
 
         events.sort_by(|a, b| a.0.inner().nonce.cmp(&b.0.inner().nonce));
         Ok(events)
@@ -86,13 +86,13 @@ impl Indexer<HyperlaneMessage> for TronMailboxIndexer {
         .await;
         let logs = raw_logs_and_meta
             .into_iter()
-            .map(|(log, log_meta)| {
-                (
-                    HyperlaneMessage::from(log.message.to_vec()).into(),
+            .map(|(log, log_meta)| -> ChainResult<_> {
+                Ok((
+                    HyperlaneMessage::read_from(&mut log.message.as_ref())?.into(),
                     log_meta,
-                )
+                ))
             })
-            .collect();
+            .collect::<ChainResult<Vec<_>>>()?;
         Ok(logs)
     }
 }
```

### rust/main/hyperlane-core/src/types/message.rs
```diff
@@ -169,7 +169,59 @@ impl HyperlaneMessage {
 
 #[cfg(test)]
 mod tests {
-    use super::HyperlaneMessage;
+    use super::{HyperlaneMessage, RawHyperlaneMessage, HYPERLANE_MESSAGE_PREFIX_LEN};
+    use crate::{Decode, H256};
+
+    fn sample_message() -> HyperlaneMessage {
+        HyperlaneMessage {
+            version: 3,
+            nonce: 42,
+            origin: 1,
+            sender: H256::repeat_byte(0x11),
+            destination: 2,
+            recipient: H256::repeat_byte(0x22),
+            body: b"payload".to_vec(),
+        }
+    }
+
+    fn valid_message_bytes() -> RawHyperlaneMessage {
+        RawHyperlaneMessage::from(&sample_message())
+    }
+
+    #[test]
+    fn read_from_valid_input_unchanged() {
+        let expected = sample_message();
+        let bytes = valid_message_bytes();
+        assert!(bytes.len() > HYPERLANE_MESSAGE_PREFIX_LEN);
+
+        let decoded = HyperlaneMessage::read_from(&mut bytes.as_slice()).expect("valid message");
+        assert_eq!(decoded, expected);
+        assert_eq!(HyperlaneMessage::from(bytes), decoded);
+    }
+
+    #[test]
+    fn read_from_empty_input_returns_err() {
+        let mut empty: &[u8] = &[];
+        assert!(HyperlaneMessage::read_from(&mut empty).is_err());
+    }
+
+    #[test]
+    fn read_from_truncated_input_returns_err() {
+        let bytes = valid_message_bytes();
+        for len in [1usize, 40, HYPERLANE_MESSAGE_PREFIX_LEN - 1] {
+            let mut truncated = &bytes[..len];
+            assert!(
+                HyperlaneMessage::read_from(&mut truncated).is_err(),
+                "expected Err for truncated len={len}"
+            );
+        }
+    }
+
+    #[test]
+    fn read_from_malformed_short_input_returns_err() {
+        let mut malformed: &[u8] = &[0u8; 50];
+        assert!(HyperlaneMessage::read_from(&mut malformed).is_err());
+    }
 
     #[ignore]
     #[test]
```
