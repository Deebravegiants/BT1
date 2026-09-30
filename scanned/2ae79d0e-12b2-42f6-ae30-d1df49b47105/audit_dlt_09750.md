# [?] fix: fix panic

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-11-06
Source: https://github.com/fedimint/fedimint/commit/76a727e41d32684f2247d889440ef24f21cb501e
Type: security-commit

## Details
fix: fix panic

## Patch
### modules/fedimint-lnv2-client/src/lib.rs
```diff
@@ -60,6 +60,7 @@ use serde::{Deserialize, Serialize};
 use serde_json::Value;
 use thiserror::Error;
 use tpe::{derive_agg_decryption_key, AggregateDecryptionKey};
+use tracing::warn;
 
 use crate::api::LightningFederationApi;
 use crate::receive_sm::{ReceiveSMCommon, ReceiveSMState, ReceiveStateMachine};
@@ -415,7 +416,9 @@ impl LightningClientModule {
                 }
             }
 
-            dbtx.commit_tx().await;
+            if let Err(e) = dbtx.commit_tx_result().await {
+                warn!("Failed to commit the updated gateway mapping to the database: {e}");
+            }
         }
     }
 
```
