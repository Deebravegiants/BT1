# [?] chore: improve logging on consensus failure

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-05-29
Source: https://github.com/fedimint/fedimint/commit/c6b734109a30ad139e88d062225e8ae5a6e81169
Type: security-commit

## Details
chore: improve logging on consensus failure

## Patch
### fedimint-server/src/consensus/engine.rs
```diff
@@ -26,7 +26,7 @@ use fedimint_core::{timing, NumPeers, PeerId};
 use futures::StreamExt;
 use rand::Rng;
 use tokio::sync::{watch, RwLock};
-use tracing::{debug, info, instrument, warn, Level};
+use tracing::{debug, error, info, instrument, warn, Level};
 
 use crate::config::ServerConfig;
 use crate::consensus::aleph_bft::backup::{BackupReader, BackupWriter};
@@ -350,7 +350,10 @@ impl ConsensusEngine {
                         .items
                         .split_at(pending_accepted_items.len());
 
-                    assert!(processed.iter().eq(pending_accepted_items.iter()));
+                    assert!(
+                        processed.iter().eq(pending_accepted_items.iter()),
+                        "Consensus Failure: pending accepted items disagree with federation consensus"
+                    );
 
                     for accepted_item in unprocessed {
                         if self.process_consensus_item(
@@ -359,7 +362,7 @@ impl ConsensusEngine {
                             accepted_item.item.clone(),
                             accepted_item.peer
                         ).await.is_err(){
-                            panic!("Rejected accepted consensus item {:?}", DebugConsensusItem(&accepted_item.item));
+                            panic!("Consensus Failure: rejected item accepted by federation consensus");
                         }
 
                         item_index += 1;
@@ -393,13 +396,16 @@ impl ConsensusEngine {
                         if self.keychain.verify(&header, &signature, to_node_index(peer)){
                             signatures.insert(peer, signature);
                         } else {
-                            warn!(target: LOG_CONSENSUS, "Received invalid signature from peer {peer}");
+                            error!(target: LOG_CONSENSUS, "Consensus Failure: invalid header signature from {peer}");
                         }
                     }
                 }
                 signed_session_outcome = self.request_signed_session_outcome(&self.federation_api, session_index) => {
-                    // We check that the session outcome we have created agrees with the federations consensus
-                    assert_eq!(header, signed_session_outcome.session_outcome.header(session_index));
+                    assert_eq!(
+                        header,
+                        signed_session_outcome.session_outcome.header(session_index),
+                        "Consensus Failure: header disagrees with federation consensus"
+                    );
 
                     return Ok(signed_session_outcome);
                 }
```
