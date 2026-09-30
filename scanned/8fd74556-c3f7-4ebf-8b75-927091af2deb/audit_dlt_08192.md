# [?] BCL: Improved deadlock prevention in using the reward cert channels (#12763)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-05-28
Source: https://github.com/anza-xyz/agave/commit/05cdbd1b36c461a7e08b2b70c4a6f66398cc2013
Type: security-commit

## Details
BCL: Improved deadlock prevention in using the reward cert channels (#12763)

## Patch
### core/src/block_creation_loop.rs
```diff
@@ -7,17 +7,15 @@
 use {
     crate::{
         banking_trace::{BankingPacketSender, BankingTracer},
+        block_creation_loop::reward_certs_handler::RewardCertsHandler,
         replay_stage::{Finalizer, ReplayStage},
     },
-    agave_votor::event::LeaderWindowInfo,
+    agave_votor::{consensus_rewards::BuildRewardCertsRespSucc, event::LeaderWindowInfo},
     agave_votor_messages::{
         consensus_message::Block,
-        reward_certificate::{
-            BuildRewardCertsRequest, BuildRewardCertsRespSucc, BuildRewardCertsResponse,
-            NotarRewardCertificate, SkipRewardCertificate,
-        },
+        reward_certificate::{NotarRewardCertificate, SkipRewardCertificate},
     },
-    crossbeam_channel::{Receiver, RecvTimeoutError, Sender, select_biased},
+    crossbeam_channel::{Receiver, select_biased},
     solana_clock::Slot,
     solana_entry::block_component::{
         BlockFooterV1, GenesisCertificate, UpdateParentV1, VersionedBlockMarker,
@@ -56,6 +54,7 @@ use {
     thiserror::Error,
 };
 
+pub(crate) mod reward_certs_handler;
 mod stats;
 
 /// Source of a leader-window notification consumed by BCL.
@@ -115,10 +114,7 @@ pub struct BlockCreationLoopConfig {
     pub record_receiver_receiver: Receiver<RecordReceiver>,
     pub optimistic_parent_receiver: Receiver<LeaderWindowInfo>,
 
-    /// Channel to send the request to build reward certs.
-    pub build_reward_certs_sender: Sender<BuildRewardCertsRequest>,
-    /// Channel to receive the built reward certs.
-    pub reward_certs_receiver: Receiver<BuildRewardCertsResponse>,
+    pub(crate) reward_certs_handler: RewardCertsHandler,
 
     /// Sender for packets to banking stage (used to re-inject transactions after sad leader handover).
     pub banking_stage_sender: BankingPacketSender,
@@ -145,8 +141,7 @@ struct LeaderContext {
     slot_status_notifier: Option<SlotStatusNotifier>,
     banking_tracer: Arc<BankingTracer>,
     replay_highest_frozen: Arc<ReplayHighestFrozen>,
-    build_reward_certs_sender: Sender<BuildRewardCertsRequest>,
-    reward_certs_receiver: Receiver<BuildRewardCertsResponse>,
+    reward_certs_handler: RewardCertsHandler,
     /// Banking-stage ingress used to reschedule transactions after sad handover.
     banking_stage_sender: BankingPacketSender,
 
@@ -226,8 +221,7 @@ fn start_loop(config: BlockCreationLoopConfig) {
         replay_highest_frozen,
         highest_parent_ready,
         optimistic_parent_receiver,
-        build_reward_certs_sender,
-        reward_certs_receiver,
+        reward_certs_handler,
         highest_finalized,
         banking_stage_sender,
     } = config;
@@ -276,8 +270,7 @@ fn start_loop(config: BlockCreationLoopConfig) {
         slot_status_notifier,
         banking_tracer,
         replay_highest_frozen,
-        build_reward_certs_sender,
-        reward_certs_receiver,
+        reward_certs_handler,
         banking_stage_sender,
         metrics: LoopMetrics::default(),
         slot_metrics: SlotMetrics::default(),
@@ -629,10 +622,9 @@ fn record_and_complete_block(
     block_timer: &mut Instant,
     block_timeout: Duration,
 ) -> Result<(), PohRecorderError> {
-    drain_stale_reward_certs(ctx, bank_slot);
-    ctx.build_reward_certs_sender
-        .send(BuildRewardCertsRequest { bank_slot })
-        .map_err(|_| PohRecorderError::ChannelDisconnected)?;
+    let reward_cert_request = ctx
+        .reward_certs_handler
+        .request_reward_certs(ctx.my_pubkey, bank_slot)?;
     let mut accumulated_txs = vec![];
     let mut records_shutdown = false;
     let window_has_moved_on = loop {
@@ -751,7 +743,9 @@ fn record_and_complete_block(
     bank.set_tick_height(max_tick_height - 1);
 
     let footer = {
-        let reward_certs = recv_reward_certs(ctx, bank_slot)?;
+        let reward_certs = ctx
+            .reward_certs_handler
+            .recv_reward_certs(ctx.my_pubkey, reward_cert_request)?;
         let BuildRewardCertsRespSucc {
             skip,
             notar,
@@ -827,49 +821,6 @@ fn process_parent_ready(
     Ok(false)
 }
 
-/// Drop reward-certificate responses left over from an older bank slot.
-fn drain_stale_reward_certs(ctx: &LeaderContext, bank_slot: Slot) {
-    for reward_cert in ctx.reward_certs_receiver.try_iter() {
-        warn!(
-            "{}: dropping stale reward cert response for bank slot {}, before starting {bank_slot}",
-            ctx.my_pubkey, reward_cert.bank_slot
-        );
-    }
-}
-
-/// Wait for the reward-certificate response for `bank_slot`, ignoring stale
-/// responses generated for banks that have already been abandoned.
-fn recv_reward_certs(
-    ctx: &LeaderContext,
-    bank_slot: Slot,
-) -> Result<BuildRewardCertsRespSucc, PohRecorderError> {
-    loop {
-        if ctx.exit.load(Ordering::Relaxed) {
-            return Err(PohRecorderError::ChannelDisconnected);
-        }
-
-        match ctx
-            .reward_certs_receiver
-            .recv_timeout(Duration::from_millis(100))
-        {
-            Ok(reward_certs) if reward_certs.bank_slot == bank_slot => {
-                break reward_certs.result.map_err(PohRecorderError::from);
-            }
-            Ok(reward_certs) => {
-                warn!(
-                    "{}: ignoring stale reward cert response for bank slot {}, expected \
-                     {bank_slot}",
-                    ctx.my_pubkey, reward_certs.bank_slot
-                );
-            }
-            Err(RecvTimeoutError::Timeout) => continue,
-            Err(RecvTimeoutError::Disconnected) => {
-                return Err(PohRecorderError::ChannelDisconnected);
-            }
-        }
-    }
-}
-
 /// Stop record intake, drain any already-reserved records, and reset PoH after
 /// failing to complete the working bank.
 fn abort_failed_working_bank(
@@ -1358,7 +1309,7 @@ mod tests {
         super::*,
         crate::banking_trace::BankingTracer,
         agave_banking_stage_ingress_types::BankingPacketReceiver,
-        agave_votor_messages::reward_certificate::{BuildRewardCertsRespError, RewardCertError},
+        agave_votor::consensus_rewards::BuildRewardCertsResponse,
         crossbeam_channel::unbounded,
         solana_bls_signatures::{BLS_SIGNATURE_AFFINE_SIZE, Signature as BLSSignature},
         solana_entry::{block_component::VersionedUpdateParent, entry_or_marker::EntryOrMarker},
@@ -1551,10 +1502,9 @@ mod tests {
 
         let (_record_sender, record_receiver) = record_channels(false);
         let (_leader_window_info_sender, leader_window_info_receiver) = unbounded();
-        let (build_reward_certs_sender, _build_reward_certs_receiver) = unbounded();
-        let (reward_certs_sender, reward_certs_receiver) = unbounded();
         let (banking_stage_sender, _banking_stage_receiver) = BankingTracer::channel_for_test();
         let bank_forks_controller = test_bank_forks_controller(bank_forks.clone());
+        let (reward_certs_handler, _receiver) = RewardCertsHandler::new();
 
         let mut ctx = LeaderContext {
             exit,
@@ -1573,8 +1523,7 @@ mod tests {
             slot_status_notifier: None,
             banking_tracer: BankingTracer::new_disabled(),
             replay_highest_frozen: Arc::new(ReplayHighestFrozen::default()),
-            build_reward_certs_sender,
-            reward_certs_receiver,
+            reward_certs_handler,
             banking_stage_sender,
             metrics: LoopMetrics::default(),
             slot_metrics: SlotMetrics::default(),
@@ -1619,27 +1568,6 @@ mod tests {
         assert!(ctx.bank_forks.read().unwrap().get(1).is_none());
         assert!(ctx.record_receiver.is_shutdown());
         assert!(ctx.record_receiver.is_safe_to_restart());
-
-        reward_certs_sender
-            .send(BuildRewardCertsResponse {
-                bank_slot: 1,
-                result: Err(BuildRewardCertsRespError::RewardCertTryNew(
-                    RewardCertError::InvalidBitmap,
-                )),
-            })
-            .unwrap();
-        reward_certs_sender
-            .send(BuildRewardCertsResponse {
-                bank_slot: 2,
-                result: Ok(BuildRewardCertsRespSucc {
-                    validators: vec![my_pubkey],
-                    ..BuildRewardCertsRespSucc::default()
-                }),
-            })
-            .unwrap();
-
-        let reward_certs = recv_reward_certs(&ctx, 2).unwrap();
-        assert_eq!(reward_certs.validators, vec![my_pubkey]);
     }
 
     #[test]
@@ -1684,12 +1612,11 @@ mod tests {
 
         let (_record_sender, record_receiver) = record_channels(false);
         let (_leader_window_info_sender, leader_window_info_receiver) = unbounded();
-        let (build_reward_certs_sender, _build_reward_certs_receiver) = unbounded();
-        let (_reward_certs_sender, reward_certs_receiver) = unbounded();
         let (banking_stage_sender, _banking_stage_receiver) = BankingTracer::channel_for_test();
         let mut genesis_cert = test_genesis_certificate();
         genesis_cert.slot = parent_bank.slot();
         let bank_forks_controller = test_bank_forks_controller(bank_forks.clone());
+        let (reward_certs_handler, _receiver) = RewardCertsHandler::new();
 
         let mut ctx = LeaderContext {
             exit,
@@ -1708,8 +1635,7 @@ mod tests {
             slot_status_notifier: None,
             banking_tracer: BankingTracer::new_disabled(),
             replay_highest_frozen: Arc::new(ReplayHighestFrozen::default()),
-            build_reward_certs_sender,
-            reward_certs_receiver,
+            reward_certs_handler,
             banking_stage_sender,
             metrics: LoopMetrics::default(),
             slot_metrics: SlotMetrics::default(),
@@ -1757,10 +1683,10 @@ mod tests {
 
         let (record_sender, record_receiver) = record_channels(false);
         let (_leader_window_info_sender, leader_window_info_receiver) = unbounded();
-        let (build_reward_certs_sender, build_reward_certs_receiver) = unbounded();
-        let (reward_certs_sender, reward_certs_receiver) = unbounded();
+        let (reward_certs_sender, _reward_certs_receiver) = unbounded();
         let (banking_stage_sender, _banking_stage_receiver) = BankingTracer::channel_for_test();
         let bank_forks_controller = test_bank_forks_controller(bank_forks.clone());
+        let (reward_certs_handler, build_reward_certs_receiver) = RewardCertsHandler::new();
 
         let mut ctx = LeaderContext {
             exit,
@@ -1779,8 +1705,7 @@ mod tests {
             slot_status_notifier: None,
             banking_tracer: BankingTracer::new_disabled(),
             replay_highest_frozen: Arc::new(ReplayHighestFrozen::default()),
-            build_reward_certs_sender,
-            reward_certs_receiver,
+            reward_certs_handler,
             banking_stage_sender,
             metrics: LoopMetrics::default(),
             slot_metrics: SlotMetrics::default(),
@@ -1800,7 +1725,6 @@ mod tests {
         let delayed_reward = std::thread::spawn(move || {
             std::thread::sleep(Duration::from_millis(300));
             let _ = reward_certs_sender.send(BuildRewardCertsResponse {
-                bank_slot: 1,
                 result: Ok(BuildRewardCertsRespSucc::default()),
             });
         });
@@ -1879,10 +1803,9 @@ mod tests {
 
         let (record_sender, record_receiver) = record_channels(false);
         let (leader_window_info_sender, leader_window_info_receiver) = unbounded();
-        let (build_reward_certs_sender, _build_reward_certs_receiver) = unbounded();
-        let (_reward_certs_sender, reward_certs_receiver) = unbounded();
         let (banking_stage_sender, banking_stage_receiver) = BankingTracer::channel_for_test();
         let bank_forks_controller = test_bank_forks_controller(bank_forks.clone());
+        let (reward_certs_handler, _receiver) = RewardCertsHandler::new();
 
         let mut ctx = LeaderContext {
             exit,
@@ -1901,8 +1824,7 @@ mod tests {
             slot_status_notifier: None,
             banking_tracer: BankingTracer::new_disabled(),
             replay_highest_frozen: Arc::new(ReplayHighestFrozen::default()),
-            build_reward_certs_sender,
-            reward_certs_receiver,
+            reward_certs_handler,
             banking_stage_sender,
             metrics: LoopMetrics::default(),
             slot_metrics: SlotMetrics::default(),
```

### core/src/block_creation_loop/reward_certs_handler.rs
```diff
@@ -0,0 +1,147 @@
+use {
+    agave_votor::consensus_rewards::{
+        BuildRewardCertsRequest, BuildRewardCertsRespSucc, BuildRewardCertsResponse,
+    },
+    crossbeam_channel::{Receiver, Sender, TryRecvError, TrySendError, bounded},
+    solana_clock::Slot,
+    solana_poh::poh_recorder::PohRecorderError,
+    solana_pubkey::Pubkey,
+};
+
+/// The request token to be used to receive responses on previously sent requests to build reward certs.
+pub(super) struct RewardCertRequest {
+    reply_receiver: Receiver<BuildRewardCertsResponse>,
+}
+
+/// Struct to handle requests to build rewards certs and receive the produced certs.
+pub(crate) struct RewardCertsHandler {
+    sender: Sender<BuildRewardCertsRequest>,
+}
+
+impl RewardCertsHandler {
+    pub(crate) fn new() -> (Self, Receiver<BuildRewardCertsRequest>) {
+        // If the rewards container is keeping up, we should only ever expect there to be 1 msg in
+        // flight.  So using a fairly small capacity to allow the rewards container to catch up if
+        // it ever falls behind.
+        const CAPACITY: usize = 16;
+
+        let (tx, rx) = bounded(CAPACITY);
+        (Self { sender: tx }, rx)
+    }
+
+    /// Tries to send a message requesting a reward cert to be built.
+    ///
+    /// Does not block trying to send a message as we have a tight deadline to produce the block
+    /// and if the rewards container is not keeping up, then we would rather not include a rewards
+    /// cert than wait.
+    ///
+    /// Returns:
+    /// - `Ok(Some(RewardCertRequest))`` if sending succeeded.  The `RewardCertRequest` can be
+    ///   used to receive a response to the build the reward cert.
+    /// - `Ok(None)` if sending failed because the channel is full i.e. the rewards container is
+    ///   not keeping up.
+    /// - `Err(PohRecorderError::ChannelDisconnected)` if the channel is to the rewards container
+    ///   is disconnected.
+    pub(super) fn request_reward_certs(
+        &mut self,
+        my_pubkey: Pubkey,
+        bank_slot: Slot,
+    ) -> Result<Option<RewardCertRequest>, PohRecorderError> {
+        let (reply_sender, reply_receiver) = bounded(1);
+        let request = BuildRewardCertsRequest {
+            bank_slot,
+            reply_sender,
+        };
+        match self.sender.try_send(request) {
+            Ok(()) => Ok(Some(RewardCertRequest { reply_receiver })),
+            Err(TrySendError::Full(_)) => {
+                warn!(
+                    "{my_pubkey} sending request to build reward cert for bank_slot={bank_slot} \
+                     failed, channel is full"
+                );
+                Ok(None)
+            }
+            Err(TrySendError::Disconnected(_)) => Err(PohRecorderError::ChannelDisconnected),
+        }
+    }
+
+    /// Tries to receive a response for an earlier request to build reward certs.
+    ///
+    /// Does not block trying to receive the response as we have a tight deadline to produce
+    /// the block and if the rewards container is not keeping up, we will rather not include any
+    /// reward certs than wait for it.
+    pub(super) fn recv_reward_certs(
+        &mut self,
+        my_pubkey: Pubkey,
+        request: Option<RewardCertRequest>,
+    ) -> Result<BuildRewardCertsRespSucc, PohRecorderError> {
+        match request {
+            None => Ok(BuildRewardCertsRespSucc::default()),
+            Some(request) => {
+                let msg = request.reply_receiver.try_recv();
+                match msg {
+                    Err(TryRecvError::Empty) => {
+                        warn!("{my_pubkey} trying to receive cert failed, channel is empty");
+                        Ok(BuildRewardCertsRespSucc::default())
+                    }
+                    Err(TryRecvError::Disconnected) => Err(PohRecorderError::ChannelDisconnected),
+                    Ok(resp) => match resp.result {
+                        Ok(res) => Ok(res),
+                        Err(err) => {
+                            error!("{my_pubkey} building reward cert failed with {err:?}");
+                            Ok(BuildRewardCertsRespSucc::default())
+                        }
+                    },
+                }
+            }
+        }
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_does_not_block() {
+        let my_pubkey = Pubkey::default();
+        let (mut handler, _receiver) = RewardCertsHandler::new();
+        handler.request_reward_certs(my_pubkey, 1).unwrap().unwrap();
+
+        let resp = handler.recv_reward_certs(my_pubkey, None).unwrap();
+        assert_eq!(resp, BuildRewardCertsRespSucc::default());
+
+        {
+            let (_reply_sender, reply_receiver) = bounded(0);
+            let request = RewardCertRequest { reply_receiver };
+            let resp = handler.recv_reward_certs(my_pubkey, Some(request)).unwrap();
+            assert_eq!(resp, BuildRewardCertsRespSucc::default());
+        }
+    }
+
+    #[test]
+    fn test_basic_functionality() {
+        let my_pubkey = Pubkey::default();
+        let (mut handler, receiver) = RewardCertsHandler::new();
+        let request = handler.request_reward_certs(my_pubkey, 1).unwrap().unwrap();
+        let validators = vec![Pubkey::new_unique(); 10];
+
+        let BuildRewardCertsRequest {
+            bank_slot: _,
+            reply_sender,
+        } = receiver.recv().unwrap();
+        reply_sender
+            .send(BuildRewardCertsResponse {
+                result: Ok(BuildRewardCertsRespSucc {
+                    skip: None,
+                    notar: None,
+                    validators: validators.clone(),
+                }),
+            })
+            .unwrap();
+        let resp = handler.recv_reward_certs(my_pubkey, Some(request)).unwrap();
+        assert!(resp.skip.is_none());
+        assert!(resp.notar.is_none());
+        assert_eq!(resp.validators, validators);
+    }
+}
```

### core/src/bls_sigverify/bls_sigverifier.rs
```diff
@@ -10,13 +10,12 @@ use {
     crate::cluster_info_vote_listener::VerifiedVoterSlotsSender,
     agave_votor::{
         consensus_metrics::ConsensusMetricsEventSender,
-        consensus_rewards::{self},
+        consensus_rewards::{self, AddVoteMessage},
         generated_cert_types::GeneratedCertTypes,
     },
     agave_votor_messages::{
         consensus_message::{CertificateType, ConsensusMessage, VoteMessage},
         migration::MigrationStatus,
-        reward_certificate::AddVoteMessage,
     },
     crossbeam_channel::{Receiver, RecvTimeoutError, Sender, TryRecvError},
     rayon::{ThreadPool, ThreadPoolBuilder},
```

### core/src/bls_sigverify/bls_vote_sigverify.rs
```diff
@@ -8,10 +8,12 @@ use {
             send_votes_to_metrics, send_votes_to_pool, send_votes_to_repair, send_votes_to_rewards,
         },
     },
-    agave_votor::{consensus_metrics::ConsensusMetricsEvent, consensus_rewards},
+    agave_votor::{
+        consensus_metrics::ConsensusMetricsEvent,
+        consensus_rewards::{self, AddVoteMessage},
+    },
     agave_votor_messages::{
         consensus_message::{ConsensusMessage, VoteMessage},
-        reward_certificate::AddVoteMessage,
         vote::Vote,
     },
     rayon::{
```

### core/src/bls_sigverify/utils.rs
```diff
@@ -4,10 +4,11 @@ use {
         bls_sigverify::{errors::SigVerifyCertError, stats::SigVerifyCertStats},
         cluster_info_vote_listener::VerifiedVoterSlotsSender,
     },
-    agave_votor::consensus_metrics::{ConsensusMetricsEvent, ConsensusMetricsEventSender},
-    agave_votor_messages::{
-        consensus_message::ConsensusMessage, reward_certificate::AddVoteMessage,
+    agave_votor::{
+        consensus_metrics::{ConsensusMetricsEvent, ConsensusMetricsEventSender},
+        consensus_rewards::AddVoteMessage,
     },
+    agave_votor_messages::consensus_message::ConsensusMessage,
     crossbeam_channel::{Sender, TrySendError},
     solana_clock::Slot,
     solana_pubkey::Pubkey,
```

### core/src/lib.rs
```diff
@@ -12,7 +12,7 @@ pub mod admin_rpc_post_init;
 pub mod banking_simulation;
 pub mod banking_stage;
 pub mod banking_trace;
-mod block_creation_loop;
+pub(crate) mod block_creation_loop;
 pub mod bls_sigverify;
 pub mod cluster_info_vote_listener;
 pub mod cluster_slots_service;
```

### core/src/tvu.rs
```diff
@@ -30,14 +30,14 @@ use {
     },
     agave_votor::{
         consensus_metrics::MAX_IN_FLIGHT_CONSENSUS_EVENTS,
+        consensus_rewards::BuildRewardCertsRequest,
         event::{LatestSwitchRequest, LeaderWindowInfo, VotorEventReceiver, VotorEventSender},
         generated_cert_types::GeneratedCertTypes,
         vote_history::VoteHistory,
         vote_history_storage::VoteHistoryStorage,
         voting_service::{VotingService as BLSVotingService, VotingServiceOverride},
         votor::{Votor, VotorConfig},
     },
-    agave_votor_messages::reward_certificate::{BuildRewardCertsRequest, BuildRewardCertsResponse},
     crossbeam_channel::{Receiver, Sender, bounded, unbounded},
     solana_client::connection_cache::ConnectionCache,
     solana_clock::Slot,
@@ -190,7 +190,6 @@ pub struct AlpenglowInitializationState {
     pub voting_service_test_override: Option<VotingServiceOverride>,
 
     // For rewards
-    pub reward_certs_sender: Sender<BuildRewardCertsResponse>,
     pub build_reward_certs_receiver: Receiver<BuildRewardCertsRequest>,
 }
 
@@ -275,7 +274,6 @@ impl Tvu {
             voting_service_test_override,
             highest_finalized,
             build_reward_certs_receiver,
-            reward_certs_sender,
         } = votor_init;
 
         // streamer and sigverify for A2A BLS messages
@@ -522,7 +520,6 @@ impl Tvu {
             event_sender: votor_event_sender.clone(),
             latest_switch_request: latest_switch_request.clone(),
             own_vote_sender: consensus_message_sender.clone(),
-            reward_certs_sender,
             repair_event_sender,
             event_receiver: votor_event_receiver,
             consensus_message_receiver,
@@ -832,7 +829,6 @@ pub mod tests {
                 thread::sleep(Duration::from_secs(1));
             }
         });
-        let (reward_certs_sender, _reward_certs_receiver) = bounded(1);
         let (_build_reward_certs_sender, build_reward_certs_receiver) = bounded(1);
         let (bank_forks_controller, bank_forks_controller_receiver) =
             BankForksControllerHandle::new();
@@ -911,7 +907,6 @@ pub mod tests {
                 bank_forks_controller,
                 bank_forks_controller_receiver,
                 build_reward_certs_receiver,
-                reward_certs_sender,
             },
         )
         .expect("assume success");
```

### core/src/validator.rs
```diff
@@ -8,7 +8,10 @@ use {
             BankingStage, transaction_scheduler::scheduler_controller::SchedulerConfig,
         },
         banking_trace::{self, BankingTracer, TraceError},
-        block_creation_loop::{BlockCreationLoop, BlockCreationLoopConfig, ReplayHighestFrozen},
+        block_creation_loop::{
+            BlockCreationLoop, BlockCreationLoopConfig, ReplayHighestFrozen,
+            reward_certs_handler::RewardCertsHandler,
+        },
         cluster_info_vote_listener::VoteTracker,
         completed_data_sets_service::CompletedDataSetsService,
         consensus::{
@@ -1491,10 +1494,8 @@ impl Validator {
         // small (but highly overprovisioned) number for performance and easier
         // debug if things go off the rails.
         let (optimistic_parent_sender, optimistic_parent_receiver) = bounded(100);
-        // There will only ever be a single msg in flight so bound channel for [`BuildRewardCertsRequest`] to 1 message.
-        let (build_reward_certs_sender, build_reward_certs_receiver) = bounded(1);
-        // There will only ever be a single msg in flight so bound channel for [`BuildRewardCertsResponse`] to 1 message.
-        let (reward_certs_sender, reward_certs_receiver) = bounded(1);
+
+        let (reward_certs_handler, build_reward_certs_receiver) = RewardCertsHandler::new();
 
         let banking_stage_sender_for_bcl = banking_tracer_channels.non_vote_sender.clone();
 
@@ -1515,8 +1516,7 @@ impl Validator {
             record_receiver_receiver,
             optimistic_parent_receiver: optimistic_parent_receiver.clone(),
             highest_finalized: highest_finalized.clone(),
-            build_reward_certs_sender,
-            reward_certs_receiver,
+            reward_certs_handler,
             banking_stage_sender: banking_stage_sender_for_bcl,
         };
         let block_creation_loop = BlockCreationLoop::new(block_creation_loop_config);
@@ -1672,7 +1672,6 @@ impl Validator {
                 voting_service_test_override: config.voting_service_test_override.clone(),
                 highest_finalized,
                 build_reward_certs_receiver,
-                reward_certs_sender,
             },
         )
         .map_err(ValidatorError::Other)?;
```

### votor-messages/src/reward_certificate.rs
```diff
@@ -1,11 +1,9 @@
 //! Defines aggregates used for vote rewards.
 
 use {
-    crate::consensus_message::VoteMessage,
     solana_bls_signatures::SignatureCompressed as BLSSignatureCompressed,
     solana_clock::Slot,
     solana_hash::Hash,
-    solana_pubkey::Pubkey,
     solana_short_vec::ShortU16,
     solana_signer_store::EncodeError,
     thiserror::Error,
@@ -117,30 +115,6 @@ impl NotarRewardCertificate {
     }
 }
 
-/// Message to add votes to the rewards container.
-#[derive(Debug)]
-pub struct AddVoteMessage {
-    /// List of [`VoteMessage`]s.
-    pub votes: Vec<VoteMessage>,
-}
-
-/// Request to build reward certificates.
-pub struct BuildRewardCertsRequest {
-    /// The bank slot which will include the built reward certs.
-    pub bank_slot: Slot,
-}
-
-/// Response when the reward certs are built successfully.
-#[derive(Default)]
-pub struct BuildRewardCertsRespSucc {
-    /// Skip reward certificate.  None if no skip votes were registered.
-    pub skip: Option<SkipRewardCertificate>,
-    /// Notar reward certificate.  None if no notar votes were registered.
-    pub notar: Option<NotarRewardCertificate>,
-    /// If at least one of the certs above is present, then this contains the slot for which the reward certs were built and the list of validators in the certs.
-    pub validators: Vec<Pubkey>,
-}
-
 /// Error returned when build reward certs fails.
 #[derive(Debug, Error)]
 pub enum BuildRewardCertsRespError {
@@ -151,11 +125,3 @@ pub enum BuildRewardCertsRespError {
     #[error("encode error {0:?}")]
     Encode(EncodeError),
 }
-
-/// Response to a [`BuildRewardCertsRequest`].
-pub struct BuildRewardCertsResponse {
-    /// The bank slot from the corresponding request.
-    pub bank_slot: Slot,
-    /// The result of building reward certs for `bank_slot`.
-    pub result: Result<BuildRewardCertsRespSucc, BuildRewardCertsRespError>,
-}
```

### votor/src/consensus_rewards.rs
```diff
@@ -2,16 +2,17 @@ use {
     agave_votor_messages::{
         consensus_message::VoteMessage,
         reward_certificate::{
-            AddVoteMessage, BuildRewardCertsRequest, BuildRewardCertsRespError,
-            BuildRewardCertsRespSucc, BuildRewardCertsResponse, NUM_SLOTS_FOR_REWARD,
+            BuildRewardCertsRespError, NUM_SLOTS_FOR_REWARD, NotarRewardCertificate,
+            SkipRewardCertificate,
         },
         vote::Vote,
     },
-    crossbeam_channel::{Receiver, Sender, select_biased},
+    crossbeam_channel::{Receiver, RecvError, Sender, select_biased},
     entry::Entry,
     solana_clock::Slot,
     solana_gossip::cluster_info::ClusterInfo,
     solana_ledger::leader_schedule_cache::LeaderScheduleCache,
+    solana_pubkey::Pubkey,
     solana_runtime::{bank::Bank, bank_forks::SharableBanks},
     std::{
         collections::BTreeMap,
@@ -70,8 +71,6 @@ struct ConsensusRewards {
     exit: Arc<AtomicBool>,
     /// Channel to receive messages to build reward certificates.
     build_reward_certs_receiver: Receiver<BuildRewardCertsRequest>,
-    /// Channel send the built reward certificates.
-    reward_certs_sender: Sender<BuildRewardCertsResponse>,
     /// Channel to receive verified votes.
     votes_receiver: Receiver<AddVoteMessage>,
 }
@@ -84,7 +83,6 @@ impl ConsensusRewards {
         sharable_banks: SharableBanks,
         exit: Arc<AtomicBool>,
         build_reward_certs_receiver: Receiver<BuildRewardCertsRequest>,
-        reward_certs_sender: Sender<BuildRewardCertsResponse>,
         votes_receiver: Receiver<AddVoteMessage>,
     ) -> Self {
         Self {
@@ -94,33 +92,46 @@ impl ConsensusRewards {
             sharable_banks,
             exit,
             build_reward_certs_receiver,
-            reward_certs_sender,
             votes_receiver,
         }
     }
 
+    fn handle_request(
+        &mut self,
+        msg: Result<BuildRewardCertsRequest, RecvError>,
+    ) -> Result<(), ()> {
+        let my_pubkey = self.cluster_info.id();
+        match msg {
+            Ok(BuildRewardCertsRequest {
+                bank_slot,
+                reply_sender,
+            }) => {
+                let resp = BuildRewardCertsResponse {
+                    result: self.build_certs(bank_slot),
+                };
+                let _ = reply_sender.send(resp).inspect_err(|_| {
+                    info!(
+                        "{my_pubkey}: channel to send reply for bank_slot={bank_slot} disconnected"
+                    );
+                });
+                Ok(())
+            }
+            Err(_) => {
+                error!("{my_pubkey}: build reward certs channel is disconnected; exiting.");
+                Err(())
+            }
+        }
+    }
+
     /// Runs a loop receiving and handling messages over different channels.
     fn run(&mut self) {
         while !self.exit.load(Ordering::Relaxed) {
             let my_pubkey = self.cluster_info.id();
             // bias messages to build certificates as that is on the critical path
             select_biased! {
                 recv(self.build_reward_certs_receiver) -> msg => {
-                    match msg {
-                        Ok(msg) => {
-                            let resp = BuildRewardCertsResponse {
-                                bank_slot: msg.bank_slot,
-                                result: self.build_certs(msg.bank_slot),
-                            };
-                            if self.reward_certs_sender.send(resp).is_err() {
-                                error!("{my_pubkey}: cert sender channel is disconnected; exiting.");
-                                break;
-                            }
-                        }
-                        Err(_) => {
-                            error!("{my_pubkey}: build reward certs channel is disconnected; exiting.");
-                            break;
-                        }
+                    if let Err(()) = self.handle_request(msg) {
+                        break;
                     }
                 }
                 recv(self.votes_receiver) -> msg => {
@@ -221,7 +232,6 @@ impl ConsensusRewardsService {
         exit: Arc<AtomicBool>,
         votes_receiver: Receiver<AddVoteMessage>,
         build_reward_certs_receiver: Receiver<BuildRewardCertsRequest>,
-        reward_certs_sender: Sender<BuildRewardCertsResponse>,
     ) -> Self {
         let handle = Builder::new()
             .name("solConsRew".to_string())
@@ -232,7 +242,6 @@ impl ConsensusRewardsService {
                     sharable_banks,
                     exit,
                     build_reward_certs_receiver,
-                    reward_certs_sender,
                     votes_receiver,
                 )
                 .run();
@@ -245,3 +254,35 @@ impl ConsensusRewardsService {
         self.handle.join()
     }
 }
+
+/// Request to build reward certificates.
+pub struct BuildRewardCertsRequest {
+    /// The bank slot which will include the built reward certs.
+    pub bank_slot: Slot,
+    /// The channel on which to send the reply.
+    pub reply_sender: Sender<BuildRewardCertsResponse>,
+}
+
+/// Response when the reward certs are built successfully.
+#[derive(Default, Debug, PartialEq, Eq)]
+pub struct BuildRewardCertsRespSucc {
+    /// Skip reward certificate.  None if no skip votes were registered.
+    pub skip: Option<SkipRewardCertificate>,
+    /// Notar reward certificate.  None if no notar votes were registered.
+    pub notar: Option<NotarRewardCertificate>,
+    /// If at least one of the certs above is present, then this contains the slot for which the reward certs were built and the list of validators in the certs.
+    pub validators: Vec<Pubkey>,
+}
+
+/// Response to a [`BuildRewardCertsRequest`].
+pub struct BuildRewardCertsResponse {
+    /// The result of building reward certs for `bank_slot`.
+    pub result: Result<BuildRewardCertsRespSucc, BuildRewardCertsRespError>,
+}
+
+/// Message to add votes to the rewards container.
+#[derive(Debug)]
+pub struct AddVoteMessage {
+    /// List of [`VoteMessage`]s.
+    pub votes: Vec<VoteMessage>,
+}
```

### votor/src/votor.rs
```diff
@@ -50,7 +50,7 @@ use {
             ConsensusMetrics, ConsensusMetricsEventReceiver, ConsensusMetricsEventSender,
         },
         consensus_pool_service::{ConsensusPoolContext, ConsensusPoolService},
-        consensus_rewards::ConsensusRewardsService,
+        consensus_rewards::{AddVoteMessage, BuildRewardCertsRequest, ConsensusRewardsService},
         event::{
             LatestSwitchRequest, LeaderWindowInfo, RepairEventSender, VotorEventReceiver,
             VotorEventSender,
@@ -64,10 +64,7 @@ use {
         voting_service::BLSOp,
         voting_utils::VotingContext,
     },
-    agave_votor_messages::{
-        consensus_message::ConsensusMessage,
-        reward_certificate::{AddVoteMessage, BuildRewardCertsRequest, BuildRewardCertsResponse},
-    },
+    agave_votor_messages::consensus_message::ConsensusMessage,
     crossbeam_channel::{Receiver, Sender},
     parking_lot::RwLock as PlRwLock,
     solana_clock::Slot,
@@ -117,7 +114,6 @@ pub struct VotorConfig {
     pub highest_parent_ready: Arc<RwLock<(Slot, (Slot, Hash))>>,
     pub event_sender: VotorEventSender,
     pub own_vote_sender: Sender<Vec<ConsensusMessage>>,
-    pub reward_certs_sender: Sender<BuildRewardCertsResponse>,
     pub repair_event_sender: RepairEventSender,
     pub latest_switch_request: LatestSwitchRequest,
 
@@ -177,7 +173,6 @@ impl Votor {
             consensus_metrics_receiver,
             reward_votes_receiver,
             build_reward_certs_receiver,
-            reward_certs_sender,
             generated_cert_types,
             highest_finalized,
             bank_forks_controller,
@@ -268,7 +263,6 @@ impl Votor {
             exit,
             reward_votes_receiver,
             build_reward_certs_receiver,
-            reward_certs_sender,
         );
 
         Self {
```
