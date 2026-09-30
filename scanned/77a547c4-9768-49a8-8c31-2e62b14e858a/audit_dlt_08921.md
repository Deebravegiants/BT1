# [?] terra/token_bridge: reentrancy protection

## Summary
Severity: Unknown
Chain: Wormhole
Component: wormhole-foundation/wormhole
Published: 2022-01-20
Source: https://github.com/wormhole-foundation/wormhole/commit/52562cacb0bd3c84b04049ae2224e73af372d69a
Type: security-commit

## Details
terra/token_bridge: reentrancy protection

commit-id:2c0bdfaf

## Patch
### terra/contracts/token-bridge/src/contract.rs
```diff
@@ -122,6 +122,9 @@ const WRAPPED_ASSET_UPDATING: &str = "updating";
 
 #[cfg_attr(not(feature = "library"), entry_point)]
 pub fn migrate(deps: DepsMut, _env: Env, _msg: MigrateMsg) -> StdResult<Response> {
+    // Clear out this just to be safe
+    wrapped_transfer_tmp(deps.storage).remove();
+
     let mut bucket = wrapped_asset_address(deps.storage);
 
     // Remove registered asset with old code ID.
@@ -175,7 +178,12 @@ pub fn instantiate(
 #[cfg_attr(not(feature = "library"), entry_point)]
 pub fn reply(deps: DepsMut, env: Env, _msg: Reply) -> StdResult<Response> {
     let cfg = config_read(deps.storage).load()?;
+
     let state = wrapped_transfer_tmp(deps.storage).load()?;
+    // NOTE: Reentrancy protection. See note in `handle_initiate_transfer_token`
+    // for why this is necessary.
+    wrapped_transfer_tmp(deps.storage).remove();
+
     let mut info = TransferInfo::deserialize(&state.message)?;
 
     // Fetch CW20 Balance post-transfer.
@@ -1018,6 +1026,15 @@ fn handle_initiate_transfer_token(
                     })?,
                 }))?;
 
+            // NOTE: Reentrancy protection. It is crucial that there's no
+            // ongoing transfer in progress here, otherwise we would override
+            // its state.  This could happen if the asset's TransferFrom handler
+            // sends us an InitiateTransfer message, which would be executed
+            // before the reply handler due the the depth-first semantics of
+            // message execution.  A simple protection mechanism is to require
+            // that there's no execution in progress. The reply handler takes
+            // care of clearing out this temporary storage when done.
+            assert!(wrapped_transfer_tmp(deps.storage).load().is_err());
             // Wrap up state to be captured by the submessage reply.
             wrapped_transfer_tmp(deps.storage).save(&TransferState {
                 previous_balance: balance.balance.to_string(),
```
