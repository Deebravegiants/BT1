# [?] Merge remote-tracking branch 'ckb-ghsa-p2gm-ffr3-w2xw/zhangsoledad/netmsg-check' into develop

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-04-11
Source: https://github.com/nervosnetwork/ckb/commit/cdc280162907649a33099bae272bb0c85b256d18
Type: security-commit

## Details
Merge remote-tracking branch 'ckb-ghsa-p2gm-ffr3-w2xw/zhangsoledad/netmsg-check' into develop

## Patch
### sync/src/relayer/get_block_proposal_process.rs
```diff
@@ -4,6 +4,7 @@ use crate::{attempt, Status, StatusCode};
 use ckb_logger::debug_target;
 use ckb_network::{CKBProtocolContext, PeerIndex};
 use ckb_types::{packed, prelude::*};
+use std::collections::HashSet;
 use std::sync::Arc;
 
 pub struct GetBlockProposalProcess<'a> {
@@ -30,21 +31,27 @@ impl<'a> GetBlockProposalProcess<'a> {
 
     pub fn execute(self) -> Status {
         let shared = self.relayer.shared();
+        let message_len = self.message.proposals().len();
         {
-            let get_block_proposal = self.message;
+            // The block proposal request is separate from uncles,
+            // so here the limit is only used to calculate the maximum value of uncles
             let limit = shared.consensus().max_block_proposals_limit()
                 * (shared.consensus().max_uncles_num() as u64);
-            if (get_block_proposal.proposals().len() as u64) > limit {
+            if message_len as u64 > limit {
                 return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
                     "GetBlockProposal proposals count({}) > consensus max_block_proposals_limit({})",
-                    get_block_proposal.proposals().len(), limit,
+                    message_len, limit,
                 ));
             }
         }
 
-        let proposals: Vec<packed::ProposalShortId> =
+        let proposals: HashSet<packed::ProposalShortId> =
             self.message.proposals().to_entity().into_iter().collect();
 
+        if proposals.len() != message_len {
+            return StatusCode::RequestDuplicate.with_context("Request duplicate proposal");
+        }
+
         let fetched_transactions = {
             let tx_pool = self.relayer.shared.shared().tx_pool_controller();
             let fetch_txs = tx_pool.fetch_txs(proposals.clone());
```

### sync/src/relayer/get_transactions_process.rs
```diff
@@ -4,6 +4,7 @@ use crate::{attempt, Status, StatusCode};
 use ckb_logger::{debug_target, trace_target};
 use ckb_network::{CKBProtocolContext, PeerIndex};
 use ckb_types::{packed, prelude::*};
+use std::collections::HashSet;
 use std::sync::Arc;
 
 pub struct GetTransactionsProcess<'a> {
@@ -29,13 +30,12 @@ impl<'a> GetTransactionsProcess<'a> {
     }
 
     pub fn execute(self) -> Status {
+        let message_len = self.message.tx_hashes().len();
         {
-            let get_transactions = self.message;
-            if get_transactions.tx_hashes().len() > MAX_RELAY_TXS_NUM_PER_BATCH {
+            if message_len > MAX_RELAY_TXS_NUM_PER_BATCH {
                 return StatusCode::ProtocolMessageIsMalformed.with_context(format!(
                     "TxHashes count({}) > MAX_RELAY_TXS_NUM_PER_BATCH({})",
-                    get_transactions.tx_hashes().len(),
-                    MAX_RELAY_TXS_NUM_PER_BATCH,
+                    message_len, MAX_RELAY_TXS_NUM_PER_BATCH,
                 ));
             }
         }
@@ -52,12 +52,16 @@ impl<'a> GetTransactionsProcess<'a> {
         let transactions: Vec<_> = {
             let tx_pool = self.relayer.shared.shared().tx_pool_controller();
 
-            let fetch_txs_with_cycles = tx_pool.fetch_txs_with_cycles(
-                tx_hashes
-                    .iter()
-                    .map(|tx_hash| packed::ProposalShortId::from_tx_hash(&tx_hash.to_entity()))
-                    .collect(),
-            );
+            let tx_hashes_set: HashSet<_> = tx_hashes
+                .iter()
+                .map(|tx_hash| packed::ProposalShortId::from_tx_hash(&tx_hash.to_entity()))
+                .collect();
+
+            if message_len != tx_hashes_set.len() {
+                return StatusCode::RequestDuplicate.with_context("Request duplicate transaction");
+            }
+
+            let fetch_txs_with_cycles = tx_pool.fetch_txs_with_cycles(tx_hashes_set);
 
             if let Err(e) = fetch_txs_with_cycles {
                 debug_target!(
```

### sync/src/relayer/mod.rs
```diff
@@ -374,7 +374,7 @@ impl Relayer {
         if !short_ids_set.is_empty() {
             let tx_pool = self.shared.shared().tx_pool_controller();
 
-            let fetch_txs = tx_pool.fetch_txs(short_ids_set.into_iter().collect());
+            let fetch_txs = tx_pool.fetch_txs(short_ids_set);
             if let Err(e) = fetch_txs {
                 return ReconstructionResult::Error(StatusCode::TxPool.with_context(e));
             }
```

### sync/src/relayer/tests/get_block_proposal_process.rs
```diff
@@ -0,0 +1,31 @@
+use crate::relayer::get_block_proposal_process::GetBlockProposalProcess;
+use crate::relayer::tests::helper::{build_chain, new_transaction, MockProtocolContext};
+use crate::StatusCode;
+use ckb_network::{PeerIndex, SupportProtocols};
+use ckb_types::packed;
+use ckb_types::prelude::*;
+use std::sync::Arc;
+
+#[test]
+fn test_duplicate() {
+    let (relayer, always_success_out_point) = build_chain(5);
+
+    let tx = new_transaction(&relayer, 1, &always_success_out_point);
+    let id = tx.proposal_short_id();
+    let snapshot = relayer.shared.shared().snapshot();
+    let hash = snapshot.tip_header().hash();
+
+    let content = packed::GetBlockProposal::new_builder()
+        .block_hash(hash)
+        .proposals(vec![id.clone(), id].into_iter().pack())
+        .build();
+    let mock_protocol_context = MockProtocolContext::new(SupportProtocols::Relay);
+    let nc = Arc::new(mock_protocol_context);
+    let peer_index: PeerIndex = 1.into();
+    let process = GetBlockProposalProcess::new(content.as_reader(), &relayer, nc, peer_index);
+
+    assert_eq!(
+        process.execute(),
+        StatusCode::RequestDuplicate.with_context("Request duplicate proposal")
+    );
+}
```

### sync/src/relayer/tests/get_transactions_process.rs
```diff
@@ -0,0 +1,27 @@
+use crate::relayer::get_transactions_process::GetTransactionsProcess;
+use crate::relayer::tests::helper::{build_chain, new_transaction, MockProtocolContext};
+use crate::StatusCode;
+use ckb_network::{PeerIndex, SupportProtocols};
+use ckb_types::packed;
+use ckb_types::prelude::*;
+use std::sync::Arc;
+
+#[test]
+fn test_duplicate() {
+    let (relayer, always_success_out_point) = build_chain(5);
+
+    let tx = new_transaction(&relayer, 1, &always_success_out_point);
+    let tx_hash = tx.hash();
+    let content = packed::GetRelayTransactions::new_builder()
+        .tx_hashes(vec![tx_hash.clone(), tx_hash].pack())
+        .build();
+    let mock_protocol_context = MockProtocolContext::new(SupportProtocols::Relay);
+    let nc = Arc::new(mock_protocol_context);
+    let peer_index: PeerIndex = 1.into();
+    let process = GetTransactionsProcess::new(content.as_reader(), &relayer, nc, peer_index);
+
+    assert_eq!(
+        process.execute(),
+        StatusCode::RequestDuplicate.with_context("Request duplicate transaction")
+    );
+}
```

### sync/src/relayer/tests/mod.rs
```diff
@@ -4,5 +4,7 @@ mod block_transactions_verifier;
 mod compact_block;
 mod compact_block_process;
 mod compact_block_verifier;
+mod get_block_proposal_process;
+mod get_transactions_process;
 mod helper;
 mod reconstruct_block;
```

### sync/src/status.rs
```diff
@@ -103,6 +103,10 @@ pub enum StatusCode {
     HeadersIsInvalid = 415,
     /// Too many unknown transactions
     TooManyUnknownTransactions = 416,
+    /// Request Genesis
+    RequestGenesis = 417,
+    /// Request Duplicate data
+    RequestDuplicate = 418,
 
     ///////////////////////////////////
     //      Warning 5xx              //
```

### sync/src/synchronizer/get_blocks_process.rs
```diff
@@ -8,6 +8,7 @@ use ckb_constant::sync::{
 use ckb_logger::debug;
 use ckb_network::{CKBProtocolContext, PeerIndex};
 use ckb_types::{packed, prelude::*};
+use std::collections::HashSet;
 
 pub struct GetBlocksProcess<'a> {
     message: packed::GetBlocksReader<'a>,
@@ -55,10 +56,20 @@ impl<'a> GetBlocksProcess<'a> {
                 .iter()
                 .take(NEW_INIT_BLOCKS_IN_TRANSIT_PER_PEER),
         };
+
+        let mut dedup = HashSet::new();
         for block_hash in iter {
             debug!("get_blocks {} from peer {:?}", block_hash, self.peer);
             let block_hash = block_hash.to_entity();
 
+            if block_hash == self.synchronizer.shared().consensus().genesis_hash() {
+                return StatusCode::RequestGenesis.with_context("Request genesis block");
+            }
+
+            if !dedup.insert(block_hash.clone()) {
+                return StatusCode::RequestDuplicate.with_context("Request duplicate block");
+            }
+
             if !active_chain.contains_block_status(&block_hash, BlockStatus::BLOCK_VALID) {
                 debug!(
                     "ignoring get_block {} request from peer={} for unverified",
```

### sync/src/tests/synchronizer/functions.rs
```diff
@@ -16,7 +16,9 @@ use ckb_types::{
         cell::resolve_transaction, BlockBuilder, BlockNumber, BlockView, EpochExt, HeaderBuilder,
         HeaderView as CoreHeaderView, TransactionBuilder, TransactionView,
     },
-    packed::{Byte32, CellInput, CellOutputBuilder, Script, SendBlockBuilder, SendHeadersBuilder},
+    packed::{
+        self, Byte32, CellInput, CellOutputBuilder, Script, SendBlockBuilder, SendHeadersBuilder,
+    },
     prelude::*,
     utilities::difficulty_to_compact,
     U256,
@@ -34,9 +36,9 @@ use std::{
 };
 
 use crate::{
-    synchronizer::{BlockFetcher, BlockProcess, HeadersProcess, Synchronizer},
+    synchronizer::{BlockFetcher, BlockProcess, GetBlocksProcess, HeadersProcess, Synchronizer},
     types::{HeaderView, HeadersSyncController, IBDState, PeerState},
-    Status, SyncShared,
+    Status, StatusCode, SyncShared,
 };
 
 fn start_chain(consensus: Option<Consensus>) -> (ChainController, Shared, Synchronizer) {
@@ -501,7 +503,7 @@ impl CKBProtocolContext for DummyNetworkContext {
     fn ban_peer(&self, _peer_index: PeerIndex, _duration: Duration, _reason: String) {}
     // Other methods
     fn protocol_id(&self) -> ProtocolId {
-        unimplemented!();
+        ProtocolId::new(1)
     }
 }
 
@@ -1105,6 +1107,43 @@ fn test_fix_last_common_header() {
     }
 }
 
+#[test]
+fn get_blocks_process() {
+    let consensus = Consensus::default();
+    let (chain_controller, shared, synchronizer) = start_chain(Some(consensus));
+
+    let num = 2;
+    for i in 1..num {
+        insert_block(&chain_controller, &shared, u128::from(i), i);
+    }
+
+    let genesis_hash = shared.consensus().genesis_hash();
+    let message_with_genesis = packed::GetBlocks::new_builder()
+        .block_hashes(vec![genesis_hash].pack())
+        .build();
+
+    let nc = mock_network_context(1);
+    let peer: PeerIndex = 1.into();
+    let process = GetBlocksProcess::new(message_with_genesis.as_reader(), &synchronizer, peer, &nc);
+    assert_eq!(
+        process.execute(),
+        StatusCode::RequestGenesis.with_context("Request genesis block")
+    );
+
+    let hash = shared.snapshot().get_block_hash(1).unwrap();
+    let message_with_dup = packed::GetBlocks::new_builder()
+        .block_hashes(vec![hash.clone(), hash].pack())
+        .build();
+
+    let nc = mock_network_context(1);
+    let peer: PeerIndex = 1.into();
+    let process = GetBlocksProcess::new(message_with_dup.as_reader(), &synchronizer, peer, &nc);
+    assert_eq!(
+        process.execute(),
+        StatusCode::RequestDuplicate.with_context("Request duplicate block")
+    );
+}
+
 #[test]
 fn test_internal_db_error() {
     use crate::utils::is_internal_db_error;
```

### tx-pool/src/service.rs
```diff
@@ -97,8 +97,8 @@ pub(crate) enum Message {
     SubmitRemoteTx(Request<(TransactionView, Cycle, PeerIndex), ()>),
     NotifyTxs(Notify<Vec<TransactionView>>),
     FreshProposalsFilter(Request<Vec<ProposalShortId>, Vec<ProposalShortId>>),
-    FetchTxs(Request<Vec<ProposalShortId>, HashMap<ProposalShortId, TransactionView>>),
-    FetchTxsWithCycles(Request<Vec<ProposalShortId>, FetchTxsWithCyclesResult>),
+    FetchTxs(Request<HashSet<ProposalShortId>, HashMap<ProposalShortId, TransactionView>>),
+    FetchTxsWithCycles(Request<HashSet<ProposalShortId>, FetchTxsWithCyclesResult>),
     GetTxPoolInfo(Request<(), TxPoolInfo>),
     FetchTxRPC(Request<Byte32, Option<(bool, TransactionView)>>),
     GetTxStatus(Request<Byte32, GetTxStatusResult>),
@@ -392,7 +392,7 @@ impl TxPoolController {
     /// Return txs for network
     pub fn fetch_txs(
         &self,
-        short_ids: Vec<ProposalShortId>,
+        short_ids: HashSet<ProposalShortId>,
     ) -> Result<HashMap<ProposalShortId, TransactionView>, AnyError> {
         let (responder, response) = oneshot::channel();
         let request = Request::call(short_ids, responder);
@@ -410,7 +410,7 @@ impl TxPoolController {
     /// Return txs with cycles
     pub fn fetch_txs_with_cycles(
         &self,
-        short_ids: Vec<ProposalShortId>,
+        short_ids: HashSet<ProposalShortId>,
     ) -> Result<FetchTxsWithCyclesResult, AnyError> {
         let (responder, response) = oneshot::channel();
         let request = Request::call(short_ids, responder);
```
