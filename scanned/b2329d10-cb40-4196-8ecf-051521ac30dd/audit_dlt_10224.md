# [?] Initialize unfinished_proposals during init_chain to prevent TOFU crash (#1518)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-10-12
Source: https://github.com/penumbra-zone/penumbra/commit/e767b20c08d1d13a7d93cfc2ffb87e161666d29f
Type: security-commit

## Details
Initialize unfinished_proposals during init_chain to prevent TOFU crash (#1518)

## Patch
### component/src/governance/component.rs
```diff
@@ -6,9 +6,10 @@ use penumbra_transaction::Transaction;
 use tendermint::abci;
 use tracing::instrument;
 
+use crate::governance::view::View as _;
 use crate::{Component, Context};
 
-use super::{check, execute};
+use super::{check, execute, proposal::ProposalList};
 
 pub struct Governance {
     state: State,
@@ -23,7 +24,12 @@ impl Governance {
 #[async_trait]
 impl Component for Governance {
     #[instrument(name = "governance", skip(self, _app_state))]
-    async fn init_chain(&mut self, _app_state: &genesis::AppState) {}
+    async fn init_chain(&mut self, _app_state: &genesis::AppState) {
+        // Initialize the unfinished proposals tracking key in the JMT.
+        self.state
+            .put_unfinished_proposals(ProposalList::default())
+            .await;
+    }
 
     #[instrument(name = "governance", skip(self, _ctx, _begin_block))]
     async fn begin_block(&mut self, _ctx: Context, _begin_block: &abci::request::BeginBlock) {}
```

### component/src/governance/view.rs
```diff
@@ -12,7 +12,10 @@ use penumbra_transaction::action::{Proposal, ProposalPayload, Vote};
 
 use crate::stake::{self, validator, View as _};
 
-use super::{proposal, state_key};
+use super::{
+    proposal::{self, ProposalList},
+    state_key,
+};
 
 impl<T: StateExt> View for T {}
 
@@ -180,6 +183,15 @@ pub trait View: StateExt {
             .proposals)
     }
 
+    /// Set all the unfinished proposal ids.
+    async fn put_unfinished_proposals(&self, unfinished_proposals: ProposalList) {
+        self.put_domain(
+            state_key::unfinished_proposals().into(),
+            unfinished_proposals,
+        )
+        .await;
+    }
+
     /// Set the state of a proposal.
     async fn put_proposal_state(&self, proposal_id: u64, state: proposal::State) -> Result<()> {
         // Set the state of the proposal
@@ -205,11 +217,7 @@ pub trait View: StateExt {
         }
 
         // Put the modified list back into the state
-        self.put_domain(
-            state_key::unfinished_proposals().into(),
-            unfinished_proposals,
-        )
-        .await;
+        self.put_unfinished_proposals(unfinished_proposals).await;
 
         Ok(())
     }
```
