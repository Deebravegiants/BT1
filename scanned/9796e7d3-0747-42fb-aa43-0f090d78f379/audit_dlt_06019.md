# [?] fix: Leaving Unknown Federation causes panic (#8396)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-03-20
Source: https://github.com/fedimint/fedimint/commit/182bebcf96c92768e3edd7cafa4b9fc1902a8c73
Type: security-commit

## Details
fix: Leaving Unknown Federation causes panic (#8396)

Currently, if the gateway operator uses the CLI to leave an unknown
federation, the gateway will panic. This fixes the bug by returning an
error instead of panicking.

## Patch
### gateway/fedimint-gateway-client/src/main.rs
```diff
@@ -189,9 +189,6 @@ impl CliError {
     /// Classify a `ServerError` into an appropriate `ErrorCode`.
     const fn classify_server_error(err: &ServerError) -> ErrorCode {
         match err {
-            // Authentication/authorization errors
-            ServerError::InvalidRequest(_) => ErrorCode::AuthFailed,
-
             // Connection and transport errors
             ServerError::Connection(_) | ServerError::Transport(_) => ErrorCode::ConnectionFailed,
 
@@ -202,7 +199,8 @@ impl CliError {
             | ServerError::InvalidRpcId(_) => ErrorCode::InvalidInput,
 
             // Internal errors (response parsing, server errors, client errors)
-            ServerError::ResponseDeserialization(_)
+            ServerError::InvalidRequest(_)
+            | ServerError::ResponseDeserialization(_)
             | ServerError::InvalidResponse(_)
             | ServerError::ServerError(_)
             | ServerError::InternalClientError(_) => ErrorCode::Internal,
```

### gateway/fedimint-gateway-server/src/federation_manager.rs
```diff
@@ -209,19 +209,30 @@ impl FederationManager {
     ) -> std::result::Result<FederationInfo, FederationNotConnected> {
         self.clients
             .get(&federation_id)
-            .expect("`FederationManager.index_to_federation` is out of sync with `FederationManager.clients`! This is a bug.")
+            .ok_or(FederationNotConnected {
+                federation_id_prefix: federation_id.to_prefix(),
+            })?
             .borrow()
             .with(|client| async move {
-                let balance_msat = client.get_balance_for_btc().await
+                let balance_msat = client
+                    .get_balance_for_btc()
+                    .await
                     // If primary module is not available, we're not really connected yet
-                    .map_err(|_err| FederationNotConnected { federation_id_prefix: federation_id.to_prefix() })?;
-
-                let config = dbtx.load_federation_config(federation_id).await.ok_or(FederationNotConnected {
-                    federation_id_prefix: federation_id.to_prefix(),
-                })?;
-                let last_backup_time = dbtx.load_backup_record(federation_id).await.ok_or(FederationNotConnected {
-                    federation_id_prefix: federation_id.to_prefix(),
-                })?;
+                    .map_err(|_err| FederationNotConnected {
+                        federation_id_prefix: federation_id.to_prefix(),
+                    })?;
+
+                let config = dbtx.load_federation_config(federation_id).await.ok_or(
+                    FederationNotConnected {
+                        federation_id_prefix: federation_id.to_prefix(),
+                    },
+                )?;
+                let last_backup_time =
+                    dbtx.load_backup_record(federation_id)
+                        .await
+                        .ok_or(FederationNotConnected {
+                            federation_id_prefix: federation_id.to_prefix(),
+                        })?;
 
                 Ok(FederationInfo {
                     federation_id,
```

### gateway/integration_tests/src/main.rs
```diff
@@ -332,7 +332,8 @@ async fn config_test(gw_type: LightningNodeType) -> anyhow::Result<()> {
                 assert_eq!(first_fed_balance_msat, Amount::ZERO);
                 almost_equal(second_fed_balance_msat.msats, pegin_amount.msats, 10_000).unwrap();
 
-                leave_federation(gw, fed_id, 1).await?;
+                leave_federation(gw, fed_id.clone(), 1).await?;
+                gw.leave_federation(FederationId::from_str(&fed_id).expect("invalid federation id")).await.expect_err("Successfully left a federation twice");
                 leave_federation(gw, new_fed_id, 2).await?;
 
                 // Rejoin new federation, verify that the balance is the same
```
