# [?] fix(ln): do not panic on a preimage status query for an outgoing contract

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/52e4ccde4f69cc62700c34d591acbc8b822ee885
Type: security-commit

## Details
fix(ln): do not panic on a preimage status query for an outgoing contract

`GET_DECRYPTED_PREIMAGE_STATUS` is a public, unauthenticated endpoint. It
resolves the contract with `wait_key_exists(ContractKey(id))`, and
`ContractKey` holds either contract variant, so the caller picks which
variant the handler ends up with. `get_incoming_contract_account` then
hit an unconditional `panic!("Contract is not an IncomingContractAccount")`
for anything that is not incoming.

`process_output` applies no validation at all to `Contract::Outgoing`, so
an attacker funds their own outgoing contract for one msat, calls the
endpoint with its id, and the handler panics. Over iroh that takes the
guardian process down.

Make `get_incoming_contract_account` return an `Option` and have the
endpoint answer a 400 for a non-incoming contract.

The sibling `AWAIT_PREIMAGE_DECRYPTION` was not affected and is left
functionally unchanged: it uses `wait_value_matches`, whose predicate
returns `false` for `FundedContract::Outgoing`, so it simply keeps
waiting rather than resolving to a contract of the wrong variant. Its
call site now carries an `expect` naming that invariant instead of
relying on a panic several frames away.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9

## Patch
### modules/fedimint-ln-server/src/lib.rs
```diff
@@ -939,7 +939,7 @@ impl ServerModule for Lightning {
                 GET_DECRYPTED_PREIMAGE_STATUS,
                 ApiVersion::new(0, 0),
                 async |module: &Lightning, context, contract_id: ContractId| -> (IncomingContractAccount, DecryptedPreimageStatus) {
-                    Ok(module.get_decrypted_preimage_status(context, contract_id).await)
+                    module.get_decrypted_preimage_status(context, contract_id).await
                 }
             },
             public_api_endpoint! {
@@ -1127,22 +1127,31 @@ impl Lightning {
         &self,
         context: &mut ApiEndpointContext,
         contract_id: ContractId,
-    ) -> (IncomingContractAccount, DecryptedPreimageStatus) {
+    ) -> Result<(IncomingContractAccount, DecryptedPreimageStatus), ApiError> {
         let f_contract = context.wait_key_exists(ContractKey(contract_id));
         let contract = f_contract.await;
-        let incoming_contract_account = Self::get_incoming_contract_account(contract);
-        match &incoming_contract_account.contract.decrypted_preimage {
-            DecryptedPreimage::Some(key) => (
-                incoming_contract_account.clone(),
-                DecryptedPreimageStatus::Some(Preimage(sha256::Hash::hash(&key.0).to_byte_array())),
-            ),
-            DecryptedPreimage::Pending => {
-                (incoming_contract_account, DecryptedPreimageStatus::Pending)
-            }
-            DecryptedPreimage::Invalid => {
-                (incoming_contract_account, DecryptedPreimageStatus::Invalid)
-            }
-        }
+        // `ContractKey` holds either contract variant and anyone can fund an
+        // outgoing contract, so the caller decides which variant we find here.
+        let incoming_contract_account =
+            Self::get_incoming_contract_account(contract).ok_or_else(|| {
+                ApiError::bad_request("Contract is not an incoming contract".to_string())
+            })?;
+        Ok(
+            match &incoming_contract_account.contract.decrypted_preimage {
+                DecryptedPreimage::Some(key) => (
+                    incoming_contract_account.clone(),
+                    DecryptedPreimageStatus::Some(Preimage(
+                        sha256::Hash::hash(&key.0).to_byte_array(),
+                    )),
+                ),
+                DecryptedPreimage::Pending => {
+                    (incoming_contract_account, DecryptedPreimageStatus::Pending)
+                }
+                DecryptedPreimage::Invalid => {
+                    (incoming_contract_account, DecryptedPreimageStatus::Invalid)
+                }
+            },
+        )
     }
 
     async fn wait_preimage_decrypted(
@@ -1162,7 +1171,8 @@ impl Lightning {
             });
 
         let decrypt_preimage = future.await;
-        let incoming_contract_account = Self::get_incoming_contract_account(decrypt_preimage);
+        let incoming_contract_account = Self::get_incoming_contract_account(decrypt_preimage)
+            .expect("the matcher above only resolves for incoming contracts");
         match incoming_contract_account
             .clone()
             .contract
@@ -1176,15 +1186,14 @@ impl Lightning {
         }
     }
 
-    fn get_incoming_contract_account(contract: ContractAccount) -> IncomingContractAccount {
-        if let FundedContract::Incoming(incoming) = contract.contract {
-            return IncomingContractAccount {
+    fn get_incoming_contract_account(contract: ContractAccount) -> Option<IncomingContractAccount> {
+        match contract.contract {
+            FundedContract::Incoming(incoming) => Some(IncomingContractAccount {
                 amount: contract.amount,
                 contract: incoming.contract,
-            };
+            }),
+            FundedContract::Outgoing(_) => None,
         }
-
-        panic!("Contract is not an IncomingContractAccount");
     }
 
     async fn list_gateways(
@@ -1390,7 +1399,7 @@ mod tests {
     use fedimint_core::encoding::{Decodable, Encodable};
     use fedimint_core::envs::BitcoinRpcConfig;
     use fedimint_core::module::registry::{ModuleDecoderRegistry, ModuleRegistry};
-    use fedimint_core::module::{Amounts, InputMeta, TransactionItemAmounts};
+    use fedimint_core::module::{Amounts, ApiEndpointContext, InputMeta, TransactionItemAmounts};
     use fedimint_core::secp256k1::{Keypair, PublicKey, SECP256K1, generate_keypair};
     use fedimint_core::task::TaskGroup;
     use fedimint_core::util::SafeUrl;
@@ -2209,6 +2218,44 @@ mod tests {
         assert_eq!(audit_item, None);
     }
 
+    /// `GET_DECRYPTED_PREIMAGE_STATUS` is unauthenticated and looks the
+    /// contract up by `ContractKey`, which holds either contract variant.
+    /// Anyone can fund an outgoing contract for a single msat and then point
+    /// the endpoint at it, so a non-incoming contract has to be answered with
+    /// an error rather than a panic.
+    #[test_log::test(tokio::test)]
+    async fn decrypted_preimage_status_rejects_an_outgoing_contract() {
+        let (server, db, _task_group) = build_server();
+
+        let outgoing_contract = FundedContract::Outgoing(OutgoingContract {
+            hash: Preimage([42u8; 32]).consensus_hash(),
+            gateway_key: random_pub_key(),
+            timelock: 1_000_000,
+            user_key: random_pub_key(),
+            cancelled: false,
+        });
+        let contract_id = outgoing_contract.contract_id();
+
+        let mut dbtx = db.begin_transaction().await;
+        dbtx.insert_new_entry(
+            &ContractKey(contract_id),
+            &ContractAccount {
+                amount: Amount { msats: 1 },
+                contract: outgoing_contract,
+            },
+        )
+        .await;
+        dbtx.commit_tx().await;
+
+        let mut context = ApiEndpointContext::new(db, false);
+        let error = server
+            .get_decrypted_preimage_status(&mut context, contract_id)
+            .await
+            .expect_err("an outgoing contract has no decrypted preimage status");
+
+        assert_eq!(error.code, 400);
+    }
+
     /// Builds a `Lightning` server module backed by an in-memory database.
     fn build_server() -> (Lightning, Database, TaskGroup) {
         let task_group = TaskGroup::new();
```
