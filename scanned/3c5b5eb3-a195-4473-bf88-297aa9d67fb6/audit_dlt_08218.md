# [?] Fix RPC tests race condition (#29589)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2023-01-10
Source: https://github.com/solana-labs/solana/commit/226e1921bd333f16a8e72e51b3b2e19bae436c15
Type: security-commit

## Details
Fix RPC tests race condition (#29589)

## Patch
### rpc/src/rpc_pubsub.rs
```diff
@@ -1,5 +1,6 @@
 //! The `pubsub` module implements a threaded subscription service on client RPC request
-
+#[cfg(test)]
+use crate::{rpc_pubsub_service, rpc_subscriptions::RpcSubscriptions};
 use {
     crate::{
         rpc::check_is_at_least_confirmed,
@@ -400,6 +401,14 @@ impl RpcSolPubSubImpl {
             })
         }
     }
+
+    #[cfg(test)]
+    pub fn block_until_processed(&self, rpc_subscriptions: &Arc<RpcSubscriptions>) {
+        let (rpc, mut receiver) = rpc_pubsub_service::test_connection(rpc_subscriptions);
+        rpc.slot_subscribe().unwrap();
+        rpc_subscriptions.notify_slot(1, 0, 0);
+        receiver.recv();
+    }
 }
 
 fn param<T: FromStr>(param_str: &str, thing: &str) -> Result<T> {
@@ -886,12 +895,7 @@ mod tests {
             }),
         )
         .unwrap();
-
-        // Make sure the subscription is processed before continuing.
-        let (rpc2, mut receiver2) = rpc_pubsub_service::test_connection(&rpc_subscriptions);
-        rpc2.slot_subscribe().unwrap();
-        rpc_subscriptions.notify_slot(1, 0, 0);
-        receiver2.recv();
+        rpc.block_until_processed(&rpc_subscriptions);
 
         let balance = {
             let bank = bank_forks.read().unwrap().working_bank();
@@ -1015,12 +1019,7 @@ mod tests {
             }),
         )
         .unwrap();
-
-        // Make sure the subscription is processed before continuing.
-        let (rpc2, mut receiver2) = rpc_pubsub_service::test_connection(&rpc_subscriptions);
-        rpc2.slot_subscribe().unwrap();
-        rpc_subscriptions.notify_slot(1, 0, 0);
-        receiver2.recv();
+        rpc.block_until_processed(&rpc_subscriptions);
 
         let ixs = system_instruction::create_nonce_account(
             &alice.pubkey(),
```

### rpc/src/rpc_subscriptions.rs
```diff
@@ -1352,7 +1352,7 @@ pub(crate) mod tests {
             false,
             AccountResult {
                 lamports: 0,
-                subscription: 1,
+                subscription: 2,
                 space: 0,
                 data: "",
             },
@@ -1370,7 +1370,7 @@ pub(crate) mod tests {
             true,
             AccountResult {
                 lamports: 1,
-                subscription: 2,
+                subscription: 4,
                 space: 1024,
                 data: "error: data too large for bs58 encoding",
             },
@@ -1406,11 +1406,7 @@ pub(crate) mod tests {
                     encoding: UiAccountEncoding::Binary,
                 }));
 
-            // Sleep here to ensure adequate time for the async thread to fully process the
-            // subscribed notification before the bank transaction is processed. Without this
-            // sleep, the bank transaction ocassionally completes first and we hang forever
-            // waiting to receive a bank notification.
-            std::thread::sleep(Duration::from_millis(100));
+            rpc.block_until_processed(&subscriptions);
 
             bank_forks
                 .read()
@@ -2746,6 +2742,7 @@ pub(crate) mod tests {
             .unwrap();
 
         assert!(subscriptions.control.account_subscribed(&alice.pubkey()));
+        rpc0.block_until_processed(&subscriptions);
 
         let tx = system_transaction::create_account(
             &mint_keypair,
@@ -2821,6 +2818,7 @@ pub(crate) mod tests {
             serde_json::from_str::<serde_json::Value>(&response).unwrap(),
         );
         rpc0.account_unsubscribe(sub_id0).unwrap();
+        rpc0.block_until_processed(&subscriptions);
 
         let sub_id1 = rpc1
             .account_subscribe(
@@ -2833,6 +2831,7 @@ pub(crate) mod tests {
                 }),
             )
             .unwrap();
+        rpc1.block_until_processed(&subscriptions);
 
         let bank2 = bank_forks.read().unwrap().get(2).unwrap();
         bank2.freeze();
@@ -2863,7 +2862,7 @@ pub(crate) mod tests {
                        "space": 16,
                     },
                },
-               "subscription": 1,
+               "subscription": 3,
            }
         });
         assert_eq!(
@@ -2942,6 +2941,7 @@ pub(crate) mod tests {
             )
             .unwrap();
         assert!(subscriptions.control.logs_subscribed(Some(&alice.pubkey())));
+        rpc_alice.block_until_processed(&subscriptions);
 
         let tx = system_transaction::create_account(
             &mint_keypair,
```
