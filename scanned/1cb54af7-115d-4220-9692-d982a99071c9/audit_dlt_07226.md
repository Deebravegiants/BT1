# [?] [Sharded-Execution] Fix a race condition while fetching the state values on a shard from a remote stateview (#10320)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2023-10-03
Source: https://github.com/aptos-labs/aptos-core/commit/63e0ba77fe1b7d6c7ae18474365476e36f8cd5b3
Type: security-commit

## Details
[Sharded-Execution] Fix a race condition while fetching the state values on a shard from a remote stateview (#10320)

[Sharded-Execution] Fix a race condition while fetching the state values on a shard from a remote stateview

## Patch
### execution/executor-service/src/remote_state_view.rs
```diff
@@ -118,6 +118,9 @@ impl RemoteStateViewClient {
     }
 
     fn pre_fetch_state_values(&self, state_keys: Vec<StateKey>) {
+        state_keys.clone().into_iter().for_each(|state_key| {
+            self.state_view.read().unwrap().insert_state_key(state_key);
+        });
         state_keys
             .chunks(REMOTE_STATE_KEY_BATCH_SIZE)
             .map(|state_keys_chunk| state_keys_chunk.to_vec())
@@ -128,9 +131,6 @@ impl RemoteStateViewClient {
                     Self::send_state_value_request(shard_id, sender, state_keys);
                 });
             });
-        state_keys.into_iter().for_each(|state_key| {
-            self.state_view.read().unwrap().insert_state_key(state_key);
-        });
     }
 
     fn send_state_value_request(
```
