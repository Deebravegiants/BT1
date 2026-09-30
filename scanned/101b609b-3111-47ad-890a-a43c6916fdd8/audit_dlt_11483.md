# [?] fix: replace panic with graceful error handling on system time failure (#724)

## Summary
Severity: Unknown
Chain: Light client
Component: a16z/helios
Published: 2025-11-10
Source: https://github.com/a16z/helios/commit/5276792966250d9c542d69b29a1087f767018b56
Type: security-commit

## Details
fix: replace panic with graceful error handling on system time failure (#724)

## Patch
### core/src/client/node.rs
```diff
@@ -134,7 +134,7 @@ impl<N: NetworkSpec, C: Consensus<N::BlockResponse>, E: ExecutionProvider<N>> No
     async fn check_head_age(&self) -> Result<(), ClientError> {
         let timestamp = SystemTime::now()
             .duration_since(UNIX_EPOCH)
-            .unwrap_or_else(|_| panic!("unreachable"))
+            .unwrap_or_default()
             .as_secs();
 
         let tag = BlockNumberOrTag::Latest.into();
```

### ethereum/consensus-core/src/consensus_core.rs
```diff
@@ -384,10 +384,7 @@ pub fn force_update<S: ConsensusSpec>(store: &mut LightClientStore<S>, current_s
 }
 
 pub fn expected_current_slot(now: SystemTime, genesis_time: u64) -> u64 {
-    let now = now
-        .duration_since(UNIX_EPOCH)
-        .unwrap_or_else(|_| panic!("unreachable"))
-        .as_secs();
+    let now = now.duration_since(UNIX_EPOCH).unwrap_or_default().as_secs();
 
     let since_genesis = now - genesis_time;
 
```

### ethereum/src/consensus.rs
```diff
@@ -489,7 +489,7 @@ impl<S: ConsensusSpec, R: ConsensusRpc<S>> Inner<S, R> {
 
         let now = SystemTime::now()
             .duration_since(UNIX_EPOCH)
-            .unwrap_or_else(|_| panic!("unreachable"))
+            .unwrap_or_default()
             .as_secs();
 
         let time_to_next_slot = next_slot_timestamp - now;
@@ -607,9 +607,9 @@ impl<S: ConsensusSpec, R: ConsensusRpc<S>> Inner<S, R> {
         let expected_time = self.slot_timestamp(slot);
         let now = SystemTime::now()
             .duration_since(UNIX_EPOCH)
-            .unwrap_or_else(|_| panic!("unreachable"));
+            .unwrap_or_default();
 
-        let delay = now - std::time::Duration::from_secs(expected_time);
+        let delay = now.saturating_sub(std::time::Duration::from_secs(expected_time));
         chrono::Duration::from_std(delay).unwrap()
     }
 
```

### linea/src/consensus.rs
```diff
@@ -133,7 +133,7 @@ impl Inner {
             {
                 let now = SystemTime::now()
                     .duration_since(UNIX_EPOCH)
-                    .unwrap_or_else(|_| panic!("unreachable"));
+                    .unwrap_or_default();
 
                 let timestamp = Duration::from_secs(block.header.timestamp);
                 let age = now.saturating_sub(timestamp);
```

### opstack/src/consensus.rs
```diff
@@ -149,7 +149,7 @@ impl Inner {
             {
                 let now = SystemTime::now()
                     .duration_since(UNIX_EPOCH)
-                    .unwrap_or_else(|_| panic!("unreachable"));
+                    .unwrap_or_default();
 
                 let timestamp = Duration::from_secs(payload.timestamp);
                 let age = now.saturating_sub(timestamp);
```
