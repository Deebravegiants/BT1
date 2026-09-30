# [?] grandpa: fix finalization race condition (#3437)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/substrate
Published: 2019-08-19
Source: https://github.com/paritytech/substrate/commit/1ba689e68ad48135712db88abdad29e4d16ceaf5
Type: security-commit

## Details
grandpa: fix finalization race condition (#3437)

* network: handle safe fork_tree::revert errors

* grandpa: deal with race conditions on finality

* network: return on fork_tree revert

## Patch
### core/finality-grandpa/src/environment.rs
```diff
@@ -795,24 +795,6 @@ where
 	}
 
 	fn finalize_block(&self, hash: Block::Hash, number: NumberFor<Block>, round: u64, commit: Commit<Block>) -> Result<(), Self::Error> {
-		use client::blockchain::HeaderBackend;
-
-		#[allow(deprecated)]
-		let blockchain = self.inner.backend().blockchain();
-		let status = blockchain.info();
-		if number <= status.finalized_number && blockchain.hash(number)? == Some(hash) {
-			// This can happen after a forced change (triggered by the finality tracker when finality is stalled), since
-			// the voter will be restarted at the median last finalized block, which can be lower than the local best
-			// finalized block.
-			warn!(target: "afg", "Re-finalized block #{:?} ({:?}) in the canonical chain, current best finalized is #{:?}",
-				  hash,
-				  number,
-				  status.finalized_number,
-			);
-
-			return Ok(());
-		}
-
 		finalize_block(
 			&*self.inner,
 			&self.authority_set,
@@ -887,6 +869,29 @@ pub(crate) fn finalize_block<B, Block: BlockT<Hash=H256>, E, RA>(
 	E: CallExecutor<Block, Blake2Hasher> + Send + Sync,
 	RA: Send + Sync,
 {
+	use client::blockchain::HeaderBackend;
+
+	#[allow(deprecated)]
+	let blockchain = client.backend().blockchain();
+	let info = blockchain.info();
+	if number <= info.finalized_number && blockchain.hash(number)? == Some(hash) {
+		// We might have a race condition on finality, since we can finalize
+		// through either sync (import justification) or through grandpa gossip.
+		// so let's make sure that this finalization request is no longer stale.
+		// This can also happen after a forced change (triggered by the finality
+		// tracker when finality is stalled), since the voter will be restarted
+		// at the median last finalized block, which can be lower than the local
+		// best finalized block.
+		warn!(target: "afg",
+			"Re-finalized block #{:?} ({:?}) in the canonical chain, current best finalized is #{:?}",
+			hash,
+			number,
+			info.finalized_number,
+		);
+
+		return Ok(());
+	}
+
 	// lock must be held through writing to DB to avoid race
 	let mut authority_set = authority_set.inner().write();
 
```

### core/network/src/protocol/sync/extra_requests.rs
```diff
@@ -18,7 +18,7 @@ use client::error::Error as ClientError;
 use crate::protocol::sync::{PeerSync, PeerSyncState};
 use fork_tree::ForkTree;
 use libp2p::PeerId;
-use log::warn;
+use log::{debug, warn};
 use sr_primitives::traits::{Block as BlockT, NumberFor, Zero};
 use std::collections::{HashMap, HashSet, VecDeque};
 use std::time::{Duration, Instant};
@@ -85,9 +85,15 @@ impl<B: BlockT> ExtraRequests<B> {
 				// this is a new root so we add it to the current `pending_requests`
 				self.pending_requests.push_back((request.0, request.1));
 			}
+			Err(fork_tree::Error::Revert) => {
+				// we have finalized further than the given request, presumably
+				// by some other part of the system (not sync). we can safely
+				// ignore the `Revert` error.
+				return;
+			},
 			Err(err) => {
-				warn!(target: "sync", "Failed to insert request {:?} into tree: {:?}", request, err);
-				return
+				debug!(target: "sync", "Failed to insert request {:?} into tree: {:?}", request, err);
+				return;
 			}
 			_ => ()
 		}
@@ -132,7 +138,20 @@ impl<B: BlockT> ExtraRequests<B> {
 		}
 
 		if best_finalized_number > self.best_seen_finalized_number {
-			self.tree.finalize_with_ancestors(best_finalized_hash, best_finalized_number, &is_descendent_of)?;
+			match self.tree.finalize_with_ancestors(
+				best_finalized_hash,
+				best_finalized_number,
+				&is_descendent_of,
+			) {
+				Err(fork_tree::Error::Revert) => {
+					// we might have finalized further already in which case we
+					// will get a `Revert` error which we can safely ignore.
+					return Ok(());
+				},
+				Err(err) => return Err(err),
+				Ok(_) => {},
+			}
+
 			self.best_seen_finalized_number = best_finalized_number;
 		}
 
```
