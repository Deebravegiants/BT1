# [?] fix(gateway-types/preconfirmed): prevent panics on malformed respose bodies

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-05-22
Source: https://github.com/software-mansion/pathfinder/commit/c14a1099ba0ae9a1d4e983ee742c05fa95a57f73
Type: security-commit

## Details
fix(gateway-types/preconfirmed): prevent panics on malformed respose bodies

## Patch
### crates/gateway-client/src/builder.rs
```diff
@@ -530,6 +530,7 @@ fn retry_condition(e: &SequencerError) -> bool {
             error!(reason=?e, "Request failed, retrying");
             true
         }
+        SequencerError::InvalidResponse(_) => false,
     }
 }
 
```

### crates/gateway-client/src/lib.rs
```diff
@@ -534,7 +534,11 @@ impl GatewayApi for Client {
             .get()
             .await?;
 
-        Ok(wire.into())
+        wire.try_into().map_err(
+            |e: starknet_gateway_types::reply::MalformedPreConfirmedResponse| {
+                SequencerError::InvalidResponse(e.to_string())
+            },
+        )
     }
 
     #[tracing::instrument(skip(self))]
```

### crates/gateway-client/src/metrics.rs
```diff
@@ -177,6 +177,9 @@ pub async fn with_metrics<T>(
             SequencerError::InvalidStarknetErrorVariant => {
                 increment_failed(meta, REASON_DECODE);
             }
+            SequencerError::InvalidResponse(_) => {
+                increment_failed(meta, REASON_DECODE);
+            }
             SequencerError::ReqwestError(e) if e.is_decode() => {
                 increment_failed(meta, REASON_DECODE);
             }
```

### crates/gateway-types/src/error.rs
```diff
@@ -17,6 +17,9 @@ pub enum SequencerError {
     /// not informative enough or bloated
     #[error("error decoding response body: invalid error variant")]
     InvalidStarknetErrorVariant,
+    /// Response body did not match its expected schema.
+    #[error("invalid sequencer response: {0}")]
+    InvalidResponse(String),
 }
 
 /// Errors related to constructing a request to the gateway.
```

### crates/gateway-types/src/reply.rs
```diff
@@ -203,71 +203,81 @@ pub enum PreConfirmedPollResponse {
     },
 }
 
-fn build_block(wire: &mut PreConfirmedPollResponseWire) -> PreConfirmedBlock {
-    PreConfirmedBlock {
+/// Returned when a `changed: true` wire response is missing a field that the
+/// variant (Delta or Full) requires.
+#[derive(Debug, thiserror::Error)]
+#[error("missing field `{0}` in pre-confirmed response")]
+pub struct MalformedPreConfirmedResponse(&'static str);
+
+fn build_block(
+    wire: &mut PreConfirmedPollResponseWire,
+) -> Result<PreConfirmedBlock, MalformedPreConfirmedResponse> {
+    Ok(PreConfirmedBlock {
         l1_gas_price: wire
             .l1_gas_price
             .take()
-            .expect("l1_gas_price missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("l1_gas_price"))?,
         l1_data_gas_price: wire
             .l1_data_gas_price
             .take()
-            .expect("l1_data_gas_price missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("l1_data_gas_price"))?,
         l2_gas_price: wire
             .l2_gas_price
             .take()
-            .expect("l2_gas_price missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("l2_gas_price"))?,
         sequencer_address: wire
             .sequencer_address
             .take()
-            .expect("sequencer_address missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("sequencer_address"))?,
         status: wire
             .status
             .take()
-            .expect("status missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("status"))?,
         timestamp: wire
             .timestamp
             .take()
-            .expect("timestamp missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("timestamp"))?,
         starknet_version: wire
             .starknet_version
             .take()
-            .expect("starknet_version missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("starknet_version"))?,
         l1_da_mode: wire
             .l1_da_mode
             .take()
-            .expect("l1_da_mode missing in pre-confirmed full block"),
+            .ok_or(MalformedPreConfirmedResponse("l1_da_mode"))?,
         transactions: std::mem::take(&mut wire.transactions),
         transaction_receipts: std::mem::take(&mut wire.transaction_receipts),
         transaction_state_diffs: std::mem::take(&mut wire.transaction_state_diffs),
-    }
+    })
 }
 
-impl From<PreConfirmedPollResponseWire> for PreConfirmedPollResponse {
-    fn from(mut wire: PreConfirmedPollResponseWire) -> Self {
+impl TryFrom<PreConfirmedPollResponseWire> for PreConfirmedPollResponse {
+    type Error = MalformedPreConfirmedResponse;
+
+    fn try_from(mut wire: PreConfirmedPollResponseWire) -> Result<Self, Self::Error> {
         if !wire.changed {
-            return Self::Unchanged;
+            return Ok(Self::Unchanged);
         }
         let identifier = wire.known_block_identifier.take().unwrap_or_default();
         if wire.status.is_some() {
             // Full: block-header fields are present.
             let block_number = wire
                 .block_number
                 .take()
-                .expect("block_number missing in pre-confirmed full block");
-            Self::Full {
+                .ok_or(MalformedPreConfirmedResponse("block_number"))?;
+            Ok(Self::Full {
                 identifier,
                 block_number,
-                block: build_block(&mut wire),
-            }
+                block: build_block(&mut wire)?,
+            })
         } else {
             // Delta: only transaction vecs; no block-header fields.
-            Self::Delta {
+            Ok(Self::Delta {
                 identifier,
                 new_transactions: wire.transactions,
                 new_receipts: wire.transaction_receipts,
                 new_state_diffs: wire.transaction_state_diffs,
-            }
+            })
         }
     }
 }
@@ -2747,7 +2757,7 @@ mod tests {
             let wire: PreConfirmedPollResponseWire =
                 serde_json::from_value(serde_json::json!({"changed": false})).unwrap();
             assert_eq!(
-                PreConfirmedPollResponse::from(wire),
+                PreConfirmedPollResponse::try_from(wire).unwrap(),
                 PreConfirmedPollResponse::Unchanged
             );
         }
@@ -2773,7 +2783,7 @@ mod tests {
                 "transaction_state_diffs": []
             });
             let wire: PreConfirmedPollResponseWire = serde_json::from_value(json).unwrap();
-            let response = PreConfirmedPollResponse::from(wire);
+            let response = PreConfirmedPollResponse::try_from(wire).unwrap();
 
             match response {
                 PreConfirmedPollResponse::Delta {
@@ -2803,7 +2813,7 @@ mod tests {
                 .insert("known_block_identifier".into(), "xyz".into());
 
             let wire: PreConfirmedPollResponseWire = serde_json::from_value(json).unwrap();
-            let response = PreConfirmedPollResponse::from(wire);
+            let response = PreConfirmedPollResponse::try_from(wire).unwrap();
 
             match response {
                 PreConfirmedPollResponse::Full {
@@ -2826,5 +2836,17 @@ mod tests {
                 other => panic!("expected Full, got {other:?}"),
             }
         }
+
+        #[test]
+        fn full_missing_block_number_returns_error() {
+            let mut json = minimal_block_json();
+            let obj = json.as_object_mut().unwrap();
+            obj.insert("changed".into(), true.into());
+            obj.remove("block_number");
+
+            let wire: PreConfirmedPollResponseWire = serde_json::from_value(json).unwrap();
+            let err = PreConfirmedPollResponse::try_from(wire).unwrap_err();
+            assert!(err.to_string().contains("block_number"));
+        }
     }
 }
```
