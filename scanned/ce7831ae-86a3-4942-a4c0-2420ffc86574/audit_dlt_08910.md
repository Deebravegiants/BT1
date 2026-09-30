# [?] fix(p2p/main_loop): fix some debug/panic messages

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2024-06-14
Source: https://github.com/software-mansion/pathfinder/commit/f19c23208878778ad373d411cd3b6626786e60f3
Type: security-commit

## Details
fix(p2p/main_loop): fix some debug/panic messages

## Patch
### crates/p2p/src/main_loop.rs
```diff
@@ -500,13 +500,13 @@ impl MainLoop {
                     channel,
                 },
             )) => {
-                tracing::debug!(%peer, %request_id, "Sync request sent");
+                tracing::debug!(%peer, %request_id, "Header sync request sent");
 
                 let _ = self
                     .pending_sync_requests
                     .headers
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Header sync request still to be pending")
                     .send(Ok(channel));
             }
             SwarmEvent::Behaviour(behaviour::Event::ClassesSync(
@@ -535,13 +535,13 @@ impl MainLoop {
                     channel,
                 },
             )) => {
-                tracing::debug!(%peer, %request_id, "Sync request sent");
+                tracing::debug!(%peer, %request_id, "Classes sync request sent");
 
                 let _ = self
                     .pending_sync_requests
                     .classes
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Classes sync request still to be pending")
                     .send(Ok(channel));
             }
             SwarmEvent::Behaviour(behaviour::Event::StateDiffsSync(
@@ -570,13 +570,13 @@ impl MainLoop {
                     channel,
                 },
             )) => {
-                tracing::debug!(%peer, %request_id, "Sync request sent");
+                tracing::debug!(%peer, %request_id, "State diff sync request sent");
 
                 let _ = self
                     .pending_sync_requests
                     .state_diffs
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("State diff sync request still to be pending")
                     .send(Ok(channel));
             }
             SwarmEvent::Behaviour(behaviour::Event::TransactionsSync(
@@ -605,13 +605,13 @@ impl MainLoop {
                     channel,
                 },
             )) => {
-                tracing::debug!(%peer, %request_id, "Sync request sent");
+                tracing::debug!(%peer, %request_id, "Transaction sync request sent");
 
                 let _ = self
                     .pending_sync_requests
                     .transactions
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Transaction sync request still to be pending")
                     .send(Ok(channel));
             }
             SwarmEvent::Behaviour(behaviour::Event::EventsSync(
@@ -640,78 +640,86 @@ impl MainLoop {
                     channel,
                 },
             )) => {
-                tracing::debug!(%peer, %request_id, "Sync request sent");
+                tracing::debug!(%peer, %request_id, "Event sync request sent");
 
                 let _ = self
                     .pending_sync_requests
                     .events
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Event sync request still to be pending")
                     .send(Ok(channel));
             }
             SwarmEvent::Behaviour(behaviour::Event::HeadersSync(
                 p2p_stream::Event::OutboundFailure {
                     request_id, error, ..
                 },
             )) => {
-                tracing::warn!(?request_id, ?error, "Outbound request failed");
+                tracing::warn!(?request_id, ?error, "Outbound header sync request failed");
                 let _ = self
                     .pending_sync_requests
                     .headers
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Header sync request still to be pending")
                     .send(Err(error.into()));
             }
             SwarmEvent::Behaviour(behaviour::Event::ClassesSync(
                 p2p_stream::Event::OutboundFailure {
                     request_id, error, ..
                 },
             )) => {
-                tracing::warn!(?request_id, ?error, "Outbound request failed");
+                tracing::warn!(?request_id, ?error, "Outbound event sync request failed");
                 let _ = self
                     .pending_sync_requests
                     .classes
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Event sync request still to be pending")
                     .send(Err(error.into()));
             }
             SwarmEvent::Behaviour(behaviour::Event::StateDiffsSync(
                 p2p_stream::Event::OutboundFailure {
                     request_id, error, ..
                 },
             )) => {
-                tracing::warn!(?request_id, ?error, "Outbound request failed");
+                tracing::warn!(
+                    ?request_id,
+                    ?error,
+                    "Outbound state diff sync request failed"
+                );
                 let _ = self
                     .pending_sync_requests
                     .state_diffs
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("State diff sync request still to be pending")
                     .send(Err(error.into()));
             }
             SwarmEvent::Behaviour(behaviour::Event::TransactionsSync(
                 p2p_stream::Event::OutboundFailure {
                     request_id, error, ..
                 },
             )) => {
-                tracing::warn!(?request_id, ?error, "Outbound request failed");
+                tracing::warn!(
+                    ?request_id,
+                    ?error,
+                    "Outbound transaction sync request failed"
+                );
                 let _ = self
                     .pending_sync_requests
                     .transactions
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Transaction sync request still to be pending")
                     .send(Err(error.into()));
             }
             SwarmEvent::Behaviour(behaviour::Event::EventsSync(
                 p2p_stream::Event::OutboundFailure {
                     request_id, error, ..
                 },
             )) => {
-                tracing::warn!(?request_id, ?error, "Outbound request failed");
+                tracing::warn!(?request_id, ?error, "Outbound event sync request failed");
                 let _ = self
                     .pending_sync_requests
                     .events
                     .remove(&request_id)
-                    .expect("Block sync request still to be pending")
+                    .expect("Event sync request still to be pending")
                     .send(Err(error.into()));
             }
             // ===========================
```
