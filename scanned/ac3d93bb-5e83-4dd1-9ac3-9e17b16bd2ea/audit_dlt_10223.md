# [?] Resolves #1798, implementing chain halt exit after commit finishes

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-02-27
Source: https://github.com/penumbra-zone/penumbra/commit/c7e57b194fede8d693fb39aace289289076276fc
Type: security-commit

## Details
Resolves #1798, implementing chain halt exit after commit finishes

## Patch
### chain/src/state_key.rs
```diff
@@ -17,3 +17,7 @@ pub fn fmd_parameters_current() -> &'static str {
 pub fn fmd_parameters_previous() -> &'static str {
     "fmd_parameters/previous"
 }
+
+pub fn halt_now() -> &'static str {
+    "halt_now"
+}
```

### chain/src/view.rs
```diff
@@ -118,6 +118,11 @@ pub trait StateReadExt: StateRead {
         // The current epoch
         Ok(Epoch::from_height(height, epoch_duration))
     }
+
+    /// Returns true if the chain should immediately halt upon the coming commit.
+    fn should_halt(&self) -> bool {
+        self.object_get::<()>(state_key::halt_now()).is_some()
+    }
 }
 
 impl<T: StateRead + ?Sized> StateReadExt for T {}
@@ -154,6 +159,11 @@ pub trait StateWriteExt: StateWrite {
     fn put_previous_fmd_parameters(&mut self, params: FmdParameters) {
         self.put(state_key::fmd_parameters_previous().into(), params)
     }
+
+    /// Signals to the consensus worker to halt after the next commit.
+    fn halt_now(&mut self) {
+        self.object_put(state_key::halt_now(), ());
+    }
 }
 
 impl<T: StateWrite + ?Sized> StateWriteExt for T {}
```

### component/src/app/mod.rs
```diff
@@ -2,7 +2,7 @@ use std::sync::Arc;
 
 use anyhow::Result;
 use penumbra_chain::params::FmdParameters;
-use penumbra_chain::{genesis, AppHash, StateWriteExt as _};
+use penumbra_chain::{genesis, AppHash, StateReadExt, StateWriteExt as _};
 use penumbra_proto::{DomainType, StateWriteProto};
 use penumbra_storage::{ArcStateDeltaExt, Snapshot, StateDelta, Storage};
 use penumbra_transaction::Transaction;
@@ -166,11 +166,21 @@ impl App {
         let state = Arc::try_unwrap(std::mem::replace(&mut self.state, Arc::new(dummy_state)))
             .expect("we have exclusive ownership of the State at commit()");
 
+        // Check if someone has signaled that we should halt.
+        let should_halt = state.should_halt();
+
         // Commit the pending writes, clearing the state.
         let jmt_root = storage
             .commit(state)
             .await
             .expect("must be able to successfully commit to storage");
+
+        // If we should halt, we should end the process here.
+        if should_halt {
+            tracing::info!("committed block when a chain halt was signaled; exiting now");
+            std::process::exit(0);
+        }
+
         let app_hash: AppHash = jmt_root.into();
 
         tracing::debug!(?app_hash, "finished committing state");
```

### component/src/governance/component.rs
```diff
@@ -1,6 +1,6 @@
 use anyhow::{Context, Result};
 use async_trait::async_trait;
-use penumbra_chain::{genesis, Epoch, StateReadExt};
+use penumbra_chain::{genesis, StateReadExt};
 use penumbra_storage::StateWrite;
 use tendermint::abci;
 use tracing::instrument;
@@ -12,22 +12,21 @@ pub struct Governance {}
 
 #[async_trait]
 impl Component for Governance {
-    #[instrument(name = "governance", skip(state, _app_state))]
-    async fn init_chain<S: StateWrite>(mut state: S, _app_state: &genesis::AppState) {
-        // Initialize the proposal counter to zero
-        state.init_proposal_counter().await;
-    }
+    #[instrument(name = "governance", skip(_state, _app_state))]
+    async fn init_chain<S: StateWrite>(_state: S, _app_state: &genesis::AppState) {}
 
     #[instrument(name = "governance", skip(_state, _begin_block))]
     async fn begin_block<S: StateWrite>(_state: S, _begin_block: &abci::request::BeginBlock) {}
 
     #[instrument(name = "governance", skip(state, _end_block))]
     async fn end_block<S: StateWrite>(mut state: S, _end_block: &abci::request::EndBlock) {
         // TODO: This will need to be altered to support dynamic epochs
-        let height = state.get_block_height().await.unwrap();
-        let epoch_duration = state.get_epoch_duration().await.unwrap();
-        let epoch = Epoch::from_height(height, epoch_duration);
-        if epoch.is_epoch_end(height) {
+        if state
+            .epoch()
+            .await
+            .unwrap()
+            .is_epoch_end(state.height().await)
+        {
             end_epoch(&mut state)
                 .await
                 .expect("end epoch should never fail");
@@ -52,64 +51,68 @@ pub async fn enact_all_passed_proposals<S: StateWrite>(mut state: S) -> Result<(
         .await
         .context("can get unfinished proposals")?
     {
-        if state.height().await
+        // TODO: this check will need to be altered when proposals have clock-time end times
+        let proposal_ready = state.height().await
             >= state
                 .proposal_voting_end(proposal_id)
                 .await?
-                .context("proposal has voting end")?
-        {
-            let current_state = state
-                .proposal_state(proposal_id)
-                .await?
-                .context("proposal has id")?;
+                .context("proposal has voting end")?;
+
+        if !proposal_ready {
+            continue;
+        }
 
-            let outcome = match current_state {
-                proposal::State::Voting => {
-                    // If the proposal is still in the voting state, tally and conclude it (this will
-                    // automatically remove it from the list of unfinished proposals)
-                    let outcome = state.current_tally(proposal_id).await?.outcome(
-                        state.total_voting_power().await?,
-                        &state.get_chain_params().await?,
-                    );
+        let current_state = state
+            .proposal_state(proposal_id)
+            .await?
+            .context("proposal has id")?;
 
-                    // If the proposal passes, enact it now (or try to: if the proposal can't be
-                    // enacted, continue onto the next one without throwing an error, just trace the
-                    // error, since proposals are allowed to fail to be enacted)
-                    if outcome.is_pass() {
-                        // IMPORTANT: We **ONLY** enact proposals that have concluded, and whose
-                        // tally is `Pass`, and whose state is not `Withdrawn`. This is the sole
-                        // place in the codebase where we prevent withdrawn proposals from being
-                        // passed!
-                        let payload = state
-                            .proposal_payload(proposal_id)
-                            .await?
-                            .context("proposal has payload")?;
-                        match state.enact_proposal(&payload).await? {
-                            Ok(()) => {}
-                            Err(error) => {
-                                tracing::error!(proposal = %proposal_id, %error, "failed to enact proposal");
-                            }
-                        };
-                    }
+        let outcome = match current_state {
+            proposal::State::Voting => {
+                // If the proposal is still in the voting state, tally and conclude it (this will
+                // automatically remove it from the list of unfinished proposals)
+                let outcome = state.current_tally(proposal_id).await?.outcome(
+                    state.total_voting_power().await?,
+                    &state.get_chain_params().await?,
+                );
 
-                    outcome.into()
-                }
-                proposal::State::Withdrawn { reason } => proposal::Outcome::Failed {
-                    withdrawn: proposal::Withdrawn::WithReason { reason },
-                },
-                proposal::State::Finished { outcome: _ } => {
-                    panic!("proposal {proposal_id} is already finished, and should have been removed from the active set");
-                }
-                proposal::State::Claimed { outcome: _ } => {
-                    panic!("proposal {proposal_id} is already claimed, and should have been removed from the active set");
+                // If the proposal passes, enact it now (or try to: if the proposal can't be
+                // enacted, continue onto the next one without throwing an error, just trace the
+                // error, since proposals are allowed to fail to be enacted)
+                if outcome.is_pass() {
+                    // IMPORTANT: We **ONLY** enact proposals that have concluded, and whose
+                    // tally is `Pass`, and whose state is not `Withdrawn`. This is the sole
+                    // place in the codebase where we prevent withdrawn proposals from being
+                    // passed!
+                    let payload = state
+                        .proposal_payload(proposal_id)
+                        .await?
+                        .context("proposal has payload")?;
+                    match state.enact_proposal(&payload).await? {
+                        Ok(()) => {}
+                        Err(error) => {
+                            tracing::error!(proposal = %proposal_id, %error, "failed to enact proposal");
+                        }
+                    };
                 }
-            };
 
-            tracing::info!(proposal = %proposal_id, outcome = ?outcome, "proposal voting concluded");
+                outcome.into()
+            }
+            proposal::State::Withdrawn { reason } => proposal::Outcome::Failed {
+                withdrawn: proposal::Withdrawn::WithReason { reason },
+            },
+            proposal::State::Finished { outcome: _ } => {
+                panic!("proposal {proposal_id} is already finished, and should have been removed from the active set");
+            }
+            proposal::State::Claimed { outcome: _ } => {
+                panic!("proposal {proposal_id} is already claimed, and should have been removed from the active set");
+            }
+        };
 
-            // Update the proposal state to reflect the outcome
-            state.put_proposal_state(proposal_id, proposal::State::Finished { outcome });
-        }
+        tracing::info!(proposal = %proposal_id, outcome = ?outcome, "proposal voting concluded");
+
+        // Update the proposal state to reflect the outcome
+        state.put_proposal_state(proposal_id, proposal::State::Finished { outcome });
     }
 
     Ok(())
```

### component/src/governance/state_key.rs
```diff
@@ -93,3 +93,7 @@ pub fn all_untallied_delegator_votes() -> &'static str {
     // Note: this has to be the prefix of the `untallied_delegator_vote` function above.
     "governance/untallied_delegator_vote/"
 }
+
+pub fn emergency_chain_halt_count() -> &'static str {
+    "governance/chain_halt_count"
+}
```

### component/src/governance/view.rs
```diff
@@ -7,7 +7,7 @@ use std::{
 use anyhow::{Context, Result};
 use async_trait::async_trait;
 use futures::{Stream, StreamExt};
-use penumbra_chain::StateReadExt as _;
+use penumbra_chain::{StateReadExt as _, StateWriteExt as _};
 use penumbra_crypto::{
     asset::{self, Amount},
     stake::{DelegationToken, IdentityKey},
@@ -33,7 +33,7 @@ pub trait StateReadExt: StateRead + crate::stake::StateReadExt {
         Ok(self
             .get_proto::<u64>(state_key::next_proposal_id())
             .await?
-            .expect("counter is initialized"))
+            .unwrap_or_default())
     }
 
     /// Get the proposal payload for a proposal.
@@ -499,17 +499,20 @@ pub trait StateReadExt: StateRead + crate::stake::StateReadExt {
 
         Ok(tally)
     }
+
+    /// Get the current chain halt count.
+    async fn emergency_chain_halt_count(&self) -> Result<u64> {
+        Ok(self
+            .get_proto(state_key::emergency_chain_halt_count())
+            .await?
+            .unwrap_or_default())
+    }
 }
 
 impl<T: StateRead + crate::stake::StateReadExt + ?Sized> StateReadExt for T {}
 
 #[async_trait]
 pub trait StateWriteExt: StateWrite {
-    /// Initialize the proposal counter at zero.
-    async fn init_proposal_counter(&mut self) {
-        self.put_proto(state_key::next_proposal_id().to_owned(), 0);
-    }
-
     /// Store a new proposal with a new proposal id.
     async fn new_proposal(&mut self, proposal: &Proposal) -> Result<u64> {
         let proposal_id = self.next_proposal_id().await?;
@@ -745,23 +748,29 @@ pub trait StateWriteExt: StateWrite {
             ProposalPayload::Emergency { halt_chain } => {
                 // If the proposal calls to halt the chain...
                 if *halt_chain {
-                    // TODO: implement emergency halt
-                    // // Check to see if the operator has set the environment variable indicating they
-                    // // wish to resume from this particular chain halt, i.e. the chain has already halted
-                    // // and they are bringing it back up again
-                    // if std::env::var("PD_RESUME_FROM_EMERGENCY_HALT_PROPOSAL")
-                    //     .ok()
-                    //     .and_then(|v| v.parse::<u64>().ok()) // value of var must be number
-                    //     .filter(|&resume_from| resume_from == proposal_id) // number must be this proposal's id (to prevent an always-on resume functionality)
-                    //     .is_some()
-                    // {
-                    //     // If so, just print an information message, and don't halt the chain
-                    //     tracing::info!(proposal = %proposal_id, %height, "resuming from emergency chain halt");
-                    // } else {
-                    //     // If not, print an informational message and immediately exit the process
-                    //     tracing::error!(proposal = %proposal_id, %height, "emergency proposal passed, calling for immediate chain halt");
-                    //     std::process::exit(0);
-                    // }
+                    // Get the current halt count
+                    let halt_count = self.emergency_chain_halt_count().await?;
+
+                    // Check to see if the operator has set the environment variable indicating they
+                    // wish to resume from this particular chain halt, i.e. the chain has already halted
+                    // and they are bringing it back up again
+                    if std::env::var("PD_RESUME_FROM_EMERGENCY_HALT_PROPOSAL")
+                        .ok()
+                        .and_then(|v| v.parse::<u64>().ok()) // value of var must be number
+                        .filter(|&resume_from| resume_from == halt_count) // number must be the same as the halt count
+                        .is_some()
+                    {
+                        // If so, just print an information message, and don't halt the chain
+                        tracing::info!("resuming from emergency chain halt #{halt_count}");
+                    } else {
+                        // If not, print an informational message and signal to the consensus worker
+                        // to halt the process after the state is committed
+                        self.increment_emergency_chain_halt_count().await?;
+                        tracing::info!(
+                            "emergency proposal passed calling for immediate chain halt"
+                        );
+                        self.halt_now();
+                    }
                 }
             }
             ProposalPayload::ParameterChange {
@@ -813,6 +822,15 @@ pub trait StateWriteExt: StateWrite {
 
         Ok(Ok(()))
     }
+
+    async fn increment_emergency_chain_halt_count(&mut self) -> Result<()> {
+        let halt_count = self.emergency_chain_halt_count().await?;
+        self.put_proto(
+            state_key::emergency_chain_halt_count().to_string(),
+            halt_count + 1,
+        );
+        Ok(())
+    }
 }
 
 impl<T: StateWrite + StateReadExt> StateWriteExt for T {}
```

### component/src/shielded_pool/component.rs
```diff
@@ -187,15 +187,7 @@ pub trait StateReadExt: StateRead {
         compact_block.block_root = block_root;
 
         // If the block ends an epoch, also close the epoch in the TCT
-        if Epoch::from_height(
-            height,
-            self.get_chain_params()
-                .await
-                .expect("chain params request must succeed")
-                .epoch_duration,
-        )
-        .is_epoch_end(height)
-        {
+        if self.epoch().await.unwrap().is_epoch_end(height) {
             tracing::debug!(?height, "end of epoch");
 
             // TODO: Put updated FMD parameters in the compact block
@@ -302,8 +294,7 @@ pub(crate) trait StateWriteExt: StateWrite {
         self.set_sct_block_anchor(height, compact_block.block_root);
         // Write the current epoch anchor, if on an epoch boundary:
         if let Some(epoch_root) = compact_block.epoch_root {
-            let epoch_duration = self.get_epoch_duration().await?;
-            let index = Epoch::from_height(height, epoch_duration).index;
+            let index = self.epoch().await?.index;
             self.set_sct_epoch_anchor(index, epoch_root);
         }
 
```
