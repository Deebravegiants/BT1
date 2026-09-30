# [?] Merge branch 'fraccaman/fix-governance-underflow' (#2459)

## Summary
Severity: Unknown
Chain: Namada
Component: anoma/namada
Published: 2024-01-29
Source: https://github.com/namada-net/namada/commit/6e41ec972df55a2563df3a6d9ffd204aa9e8a6b5
Type: security-commit

## Details
Merge branch 'fraccaman/fix-governance-underflow' (#2459)

* origin/fraccaman/fix-governance-underflow:
  add changelog
  check for duplicate in pgf action proposals
  restrict delegation field
  validate vote key in governance vp
  avoid duplicate addresses in pgf steward proposal, use btreeset instead of hashset
  use validator voting power instead of total voting power
  avoid logging an underflow, more underflow checks

## Patch
### .changelog/unreleased/bug-fixes/2459-fix-governance-underflow.md
```diff
@@ -0,0 +1,2 @@
+- Fixing several bugs in how governance and pgf transactions are handled and
+  validated. ([\#2459](https://github.com/anoma/namada/pull/2459))
\ No newline at end of file
```

### crates/apps/src/lib/client/rpc.rs
```diff
@@ -2855,14 +2855,18 @@ pub async fn compute_proposal_votes<
                 &vote.validator,
                 epoch,
             )
-            .await
-            .unwrap_or_default();
+            .await;
 
-            delegators_vote.insert(vote.delegator.clone(), vote.data.into());
-            delegator_voting_power
-                .entry(vote.delegator.clone())
-                .or_default()
-                .insert(vote.validator, delegator_stake);
+            if let Some(stake) = delegator_stake {
+                delegators_vote
+                    .insert(vote.delegator.clone(), vote.data.into());
+                delegator_voting_power
+                    .entry(vote.delegator.clone())
+                    .or_default()
+                    .insert(vote.validator, stake);
+            } else {
+                continue;
+            }
         }
     }
 
```

### crates/apps/src/lib/node/ledger/shell/governance.rs
```diff
@@ -24,6 +24,7 @@ use namada::types::address::Address;
 use namada::types::encode;
 use namada::types::storage::Epoch;
 use namada::{ibc, token};
+use namada_sdk::proof_of_stake::storage::read_validator_stake;
 
 use super::utils::force_read;
 use super::*;
@@ -127,7 +128,7 @@ where
                     ProposalType::PGFPayment(payments) => {
                         let native_token =
                             &shell.wl_storage.get_native_token()?;
-                        let result = execute_pgf_payment_proposal(
+                        let result = execute_pgf_funding_proposal(
                             &mut shell.wl_storage,
                             native_token,
                             payments,
@@ -242,7 +243,8 @@ where
             let vote_data = vote.data.clone();
 
             let validator_stake =
-                read_total_stake(storage, params, epoch).unwrap_or_default();
+                read_validator_stake(storage, params, &validator, epoch)
+                    .unwrap_or_default();
 
             validators_vote.insert(validator.clone(), vote_data.into());
             validator_voting_power.insert(validator, validator_stake);
@@ -255,14 +257,17 @@ where
                 source: delegator.clone(),
                 validator: validator.clone(),
             };
-            let delegator_stake =
-                bond_amount(storage, &bond_id, epoch).unwrap_or_default();
-
-            delegators_vote.insert(delegator.clone(), vote_data.into());
-            delegator_voting_power
-                .entry(delegator)
-                .or_default()
-                .insert(validator, delegator_stake);
+            let delegator_stake = bond_amount(storage, &bond_id, epoch);
+
+            if let Ok(stake) = delegator_stake {
+                delegators_vote.insert(delegator.clone(), vote_data.into());
+                delegator_voting_power
+                    .entry(delegator)
+                    .or_default()
+                    .insert(validator, stake);
+            } else {
+                continue;
+            }
         }
     }
 
@@ -334,7 +339,7 @@ where
 
 fn execute_pgf_steward_proposal<S>(
     storage: &mut S,
-    stewards: HashSet<AddRemove<Address>>,
+    stewards: BTreeSet<AddRemove<Address>>,
 ) -> Result<bool>
 where
     S: StorageRead + StorageWrite,
@@ -357,18 +362,18 @@ where
     Ok(true)
 }
 
-fn execute_pgf_payment_proposal<D, H>(
+fn execute_pgf_funding_proposal<D, H>(
     storage: &mut WlStorage<D, H>,
     token: &Address,
-    payments: Vec<PGFAction>,
+    fundings: BTreeSet<PGFAction>,
     proposal_id: u64,
 ) -> Result<bool>
 where
     D: DB + for<'iter> DBIter<'iter> + Sync + 'static,
     H: StorageHasher + Sync + 'static,
 {
-    for payment in payments {
-        match payment {
+    for funding in fundings {
+        match funding {
             PGFAction::Continuous(action) => match action {
                 AddRemove::Add(target) => {
                     pgf_storage::fundings_handle().insert(
@@ -377,8 +382,8 @@ where
                         StoragePgfFunding::new(target.clone(), proposal_id),
                     )?;
                     tracing::info!(
-                        "Execute ContinousPgf from proposal id {}: set {} to \
-                         {}.",
+                        "Added/Updated ContinousPgf from proposal id {}: set \
+                         {} to {}.",
                         proposal_id,
                         target.amount().to_string_native(),
                         target.target()
@@ -388,7 +393,7 @@ where
                     pgf_storage::fundings_handle()
                         .remove(storage, &target.target())?;
                     tracing::info!(
-                        "Execute ContinousPgf from proposal id {}: set {} to \
+                        "Removed ContinousPgf from proposal id {}: set {} to \
                          {}.",
                         proposal_id,
                         target.amount().to_string_native(),
```

### crates/governance/src/lib.rs
```diff
@@ -13,7 +13,7 @@ pub mod storage;
 pub mod utils;
 
 pub use storage::proposal::{InitProposalData, ProposalType, VoteProposalData};
-pub use storage::vote::{ProposalVote, VoteType};
+pub use storage::vote::ProposalVote;
 pub use storage::{init_proposal, is_proposal_accepted, vote_proposal};
 
 /// The governance internal address
```

### crates/governance/src/storage/keys.rs
```diff
@@ -438,7 +438,7 @@ pub fn get_proposal_vote_prefix_key(id: u64) -> Key {
         .expect("Cannot obtain a storage key")
 }
 
-/// Get proposal code key
+/// Get the vote key for a specific proposal id
 pub fn get_vote_proposal_key(
     id: u64,
     voter_address: Address,
```

### crates/governance/src/storage/proposal.rs
```diff
@@ -1,4 +1,4 @@
-use std::collections::{BTreeMap, HashSet};
+use std::collections::{BTreeMap, BTreeSet};
 use std::fmt::Display;
 
 use borsh::{BorshDeserialize, BorshSerialize};
@@ -76,9 +76,9 @@ pub struct VoteProposalData {
     pub id: u64,
     /// The proposal vote
     pub vote: ProposalVote,
-    /// The proposal author address
+    /// The proposal voter address
     pub voter: Address,
-    /// Delegator addreses
+    /// Validators to who the voter has delegations to
     pub delegations: Vec<Address>,
 }
 
@@ -103,7 +103,7 @@ impl TryFrom<PgfStewardProposal> for InitProposalData {
 
     fn try_from(value: PgfStewardProposal) -> Result<Self, Self::Error> {
         let extra_data =
-            HashSet::<AddRemove<Address>>::try_from(value.data).unwrap();
+            BTreeSet::<AddRemove<Address>>::try_from(value.data).unwrap();
 
         Ok(InitProposalData {
             id: value.proposal.id,
@@ -121,7 +121,7 @@ impl TryFrom<PgfFundingProposal> for InitProposalData {
     type Error = ProposalError;
 
     fn try_from(value: PgfFundingProposal) -> Result<Self, Self::Error> {
-        let continous_fundings = value
+        let mut continous_fundings = value
             .data
             .continuous
             .iter()
@@ -133,23 +133,23 @@ impl TryFrom<PgfFundingProposal> for InitProposalData {
                     PGFAction::Continuous(AddRemove::Add(target))
                 }
             })
-            .collect::<Vec<PGFAction>>();
+            .collect::<BTreeSet<PGFAction>>();
 
         let retro_fundings = value
             .data
             .retro
             .iter()
             .cloned()
             .map(PGFAction::Retro)
-            .collect::<Vec<PGFAction>>();
+            .collect::<BTreeSet<PGFAction>>();
 
-        let extra_data = [continous_fundings, retro_fundings].concat();
+        continous_fundings.extend(retro_fundings);
 
         Ok(InitProposalData {
             id: value.proposal.id,
             content: Hash::default(),
             author: value.proposal.author,
-            r#type: ProposalType::PGFPayment(extra_data),
+            r#type: ProposalType::PGFPayment(continous_fundings), /* here continous_fundings is contains also the retro funding */
             voting_start_epoch: value.proposal.voting_start_epoch,
             voting_end_epoch: value.proposal.voting_end_epoch,
             grace_epoch: value.proposal.grace_epoch,
@@ -197,9 +197,9 @@ pub enum ProposalType {
     /// Default governance proposal with the optional wasm code
     Default(Option<Hash>),
     /// PGF stewards proposal
-    PGFSteward(HashSet<AddRemove<Address>>),
+    PGFSteward(BTreeSet<AddRemove<Address>>),
     /// PGF funding proposal
-    PGFPayment(Vec<PGFAction>),
+    PGFPayment(BTreeSet<PGFAction>),
 }
 
 /// An add or remove action for PGF
@@ -369,6 +369,9 @@ impl borsh::BorshSchema for PGFIbcTarget {
     BorshDeserialize,
     Serialize,
     Deserialize,
+    Eq,
+    Ord,
+    PartialOrd,
 )]
 pub enum PGFAction {
     /// A continuous payment
@@ -401,11 +404,11 @@ pub enum ProposalTypeError {
     InvalidProposalType,
 }
 
-impl TryFrom<StewardsUpdate> for HashSet<AddRemove<Address>> {
+impl TryFrom<StewardsUpdate> for BTreeSet<AddRemove<Address>> {
     type Error = ProposalTypeError;
 
     fn try_from(value: StewardsUpdate) -> Result<Self, Self::Error> {
-        let mut data = HashSet::default();
+        let mut data = BTreeSet::default();
 
         if value.add.is_some() {
             data.insert(AddRemove::Add(value.add.unwrap()));
@@ -613,12 +616,12 @@ pub mod testing {
     pub fn arb_proposal_type() -> impl Strategy<Value = ProposalType> {
         prop_oneof![
             option::of(arb_hash()).prop_map(ProposalType::Default),
-            collection::hash_set(
+            collection::btree_set(
                 arb_add_remove(arb_non_internal_address()),
                 0..10,
             )
             .prop_map(ProposalType::PGFSteward),
-            collection::vec(arb_pgf_action(), 0..10)
+            collection::btree_set(arb_pgf_action(), 0..10)
                 .prop_map(ProposalType::PGFPayment),
         ]
     }
```

### crates/governance/src/storage/vote.rs
```diff
@@ -23,26 +23,6 @@ pub enum ProposalVote {
     Abstain,
 }
 
-/// The type of a governance vote with the optional associated Memo
-#[derive(
-    Debug,
-    Clone,
-    PartialEq,
-    BorshSerialize,
-    BorshDeserialize,
-    Eq,
-    Serialize,
-    Deserialize,
-)]
-pub enum VoteType {
-    /// A default vote without Memo
-    Default,
-    /// A vote for the PGF stewards
-    PGFSteward,
-    /// A vote for a PGF payment proposal
-    PGFPayment,
-}
-
 impl ProposalVote {
     /// Check if a vote is yay
     pub fn is_yay(&self) -> bool {
```

### crates/namada/src/ledger/governance/mod.rs
```diff
@@ -5,10 +5,14 @@ pub mod utils;
 use std::collections::BTreeSet;
 
 use borsh::BorshDeserialize;
-use namada_governance::storage::proposal::{AddRemove, ProposalType};
+use namada_governance::storage::proposal::{
+    AddRemove, PGFAction, ProposalType,
+};
 use namada_governance::storage::{is_proposal_accepted, keys as gov_storage};
 use namada_governance::utils::is_valid_validator_voting_period;
+use namada_governance::ProposalVote;
 use namada_proof_of_stake::is_validator;
+use namada_proof_of_stake::queries::find_delegations;
 use namada_state::StorageRead;
 use namada_tx::Tx;
 use namada_vp_env::VpEnv;
@@ -40,8 +44,6 @@ pub enum Error {
     EmptyProposalField(String),
     #[error("Vote key is not valid: {0}")]
     InvalidVoteKey(String),
-    #[error("Vote type is not compatible with proposal type.")]
-    InvalidVoteType,
 }
 
 /// Governance VP
@@ -70,11 +72,12 @@ where
         verifiers: &BTreeSet<Address>,
     ) -> Result<bool> {
         let (is_valid_keys_set, set_count) =
-            self.is_valid_key_set(keys_changed)?;
+            self.is_valid_init_proposal_key_set(keys_changed)?;
         if !is_valid_keys_set {
             tracing::info!("Invalid changed governance key set");
             return Ok(false);
         };
+
         let native_token = self.ctx.pre().get_native_token()?;
 
         Ok(keys_changed.iter().all(|key| {
@@ -137,7 +140,10 @@ where
     H: 'static + namada_state::StorageHasher,
     CA: 'static + WasmCacheAccess,
 {
-    fn is_valid_key_set(&self, keys: &BTreeSet<Key>) -> Result<(bool, u64)> {
+    fn is_valid_init_proposal_key_set(
+        &self,
+        keys: &BTreeSet<Key>,
+    ) -> Result<(bool, u64)> {
         let counter_key = gov_storage::get_counter_key();
         let pre_counter: u64 = self.force_read(&counter_key, ReadType::Pre)?;
         let post_counter: u64 =
@@ -211,6 +217,42 @@ where
             return Ok(false);
         }
 
+        let vote_key = gov_storage::get_vote_proposal_key(
+            proposal_id,
+            voter_address.clone(),
+            delegation_address.clone(),
+        );
+
+        if self
+            .force_read::<ProposalVote>(&vote_key, ReadType::Post)
+            .is_err()
+        {
+            return Err(Error::InvalidVoteKey(key.to_string()));
+        }
+
+        // TODO: We should refactor this by modifying the vote proposal tx
+        let all_delegations_are_valid = if let Ok(delegations) =
+            find_delegations(&self.ctx.pre(), voter_address, &current_epoch)
+        {
+            if delegations.is_empty() {
+                return Ok(false);
+            } else {
+                delegations.iter().all(|(address, _)| {
+                    let vote_key = gov_storage::get_vote_proposal_key(
+                        proposal_id,
+                        voter_address.clone(),
+                        address.clone(),
+                    );
+                    self.ctx.post().has_key(&vote_key).unwrap_or(false)
+                })
+            }
+        } else {
+            return Ok(false);
+        };
+        if !all_delegations_are_valid {
+            return Ok(false);
+        }
+
         // Voted outside of voting window. We dont check for validator because
         // if the proposal type is validator, we need to let
         // them vote for the entire voting window.
@@ -291,39 +333,99 @@ where
 
         match proposal_type {
             ProposalType::PGFSteward(stewards) => {
-                let steward_added = stewards
+                let stewards_added = stewards
                     .iter()
-                    .filter_map(|steward| match steward {
-                        AddRemove::Add(address) => Some(address),
-                        AddRemove::Remove(_) => None,
+                    .filter_map(|pgf_action| match pgf_action {
+                        AddRemove::Add(address) => Some(address.clone()),
+                        _ => None,
                     })
-                    .cloned()
                     .collect::<Vec<Address>>();
+                let total_stewards_added = stewards_added.len() as u64;
 
-                if steward_added.len() > 1 {
+                let all_pgf_action_addresses = stewards
+                    .iter()
+                    .map(|steward| match steward {
+                        AddRemove::Add(address) => address,
+                        AddRemove::Remove(address) => address,
+                    })
+                    .collect::<BTreeSet<&Address>>()
+                    .len();
+
+                // we allow only a single steward to be added
+                if total_stewards_added > 1 {
                     Ok(false)
-                } else if steward_added.is_empty() {
-                    return Ok(stewards.len() < MAX_PGF_ACTIONS);
+                } else if total_stewards_added == 0 {
+                    let is_valid_total_pgf_actions =
+                        stewards.len() < MAX_PGF_ACTIONS;
+                    return Ok(is_valid_total_pgf_actions);
+                } else if let Some(address) = stewards_added.first() {
+                    let author_key = gov_storage::get_author_key(proposal_id);
+                    let author = self
+                        .force_read::<Address>(&author_key, ReadType::Post)?;
+                    let is_valid_author = address.eq(&author);
+
+                    let stewards_addresses_are_unique =
+                        stewards.len() == all_pgf_action_addresses;
+                    let is_valid_total_pgf_actions =
+                        all_pgf_action_addresses < MAX_PGF_ACTIONS;
+
+                    return Ok(is_valid_author
+                        && stewards_addresses_are_unique
+                        && is_valid_total_pgf_actions);
                 } else {
-                    match steward_added.get(0) {
-                        Some(address) => {
-                            let author_key =
-                                gov_storage::get_author_key(proposal_id);
-                            let author =
-                                self.force_read(&author_key, ReadType::Post)?;
-                            return Ok(stewards.len() < MAX_PGF_ACTIONS
-                                && address.eq(&author));
-                        }
-                        None => return Ok(false),
-                    }
+                    return Ok(false);
                 }
             }
-            ProposalType::PGFPayment(payments) => {
-                if payments.len() > MAX_PGF_ACTIONS {
-                    Ok(false)
-                } else {
-                    Ok(true)
-                }
+            ProposalType::PGFPayment(fundings) => {
+                // collect all the funding target that we have to add and are
+                // unique
+                let are_continous_add_targets_unique = fundings
+                    .iter()
+                    .filter_map(|funding| match funding {
+                        PGFAction::Continuous(AddRemove::Add(target)) => {
+                            Some(target.target().to_lowercase())
+                        }
+                        _ => None,
+                    })
+                    .collect::<BTreeSet<String>>();
+
+                // collect all the funding target that we have to remove and are
+                // unique
+                let are_continous_remove_targets_unique = fundings
+                    .iter()
+                    .filter_map(|funding| match funding {
+                        PGFAction::Continuous(AddRemove::Remove(target)) => {
+                            Some(target.target().to_lowercase())
+                        }
+                        _ => None,
+                    })
+                    .collect::<BTreeSet<String>>();
+
+                let total_retro_targerts = fundings
+                    .iter()
+                    .filter(|funding| matches!(funding, PGFAction::Retro(_)))
+                    .count();
+
+                let is_total_fundings_valid = fundings.len() < MAX_PGF_ACTIONS;
+
+                // check that they are unique by checking that the set of add
+                // plus the set of remove plus the set of retro is equal to the
+                // total fundings
+                let are_continous_fundings_unique =
+                    are_continous_add_targets_unique.len()
+                        + are_continous_remove_targets_unique.len()
+                        + total_retro_targerts
+                        == fundings.len();
+
+                // can't remove and add the same target in the same proposal
+                let are_targets_unique = are_continous_add_targets_unique
+                    .intersection(&are_continous_remove_targets_unique)
+                    .count() as u64
+                    == 0;
+
+                Ok(is_total_fundings_valid
+                    && are_continous_fundings_unique
+                    && are_targets_unique)
             }
             _ => Ok(true), // default proposal
         }
@@ -397,17 +499,19 @@ where
         if !is_valid_grace_epoch {
             tracing::info!(
                 "Expected min duration between the end and grace epoch \
-                 {min_grace_epoch}, but got {}",
-                grace_epoch - end_epoch
+                 {min_grace_epoch}, but got grace = {}, end = {}",
+                grace_epoch,
+                end_epoch
             );
         }
         let is_valid_max_proposal_period = start_epoch < grace_epoch
             && grace_epoch.0 - start_epoch.0 <= max_proposal_period;
         if !is_valid_max_proposal_period {
             tracing::info!(
                 "Expected max duration between the start and grace epoch \
-                 {max_proposal_period}, but got {}",
-                grace_epoch - start_epoch
+                 {max_proposal_period}, but got grace ={}, start = {}",
+                grace_epoch,
+                start_epoch
             );
         }
 
@@ -512,8 +616,11 @@ where
             self.force_read(&funds_key, ReadType::Post)?;
 
         if let Some(pre_balance) = pre_balance {
-            Ok(post_funds >= min_funds_parameter
-                && post_balance - pre_balance == post_funds)
+            let is_post_funds_greater_than_minimum =
+                post_funds >= min_funds_parameter;
+            let is_valid_funds = post_balance >= pre_balance
+                && post_balance - pre_balance == post_funds;
+            Ok(is_post_funds_greater_than_minimum && is_valid_funds)
         } else {
             Ok(post_funds >= min_funds_parameter && post_balance == post_funds)
         }
```

### crates/namada/src/vm/host_env.rs
```diff
@@ -43,6 +43,7 @@ use crate::vm::{HostRef, MutHostRef};
 
 /// These runtime errors will abort tx WASM execution immediately
 #[allow(missing_docs)]
+#[allow(clippy::result_large_err)]
 #[derive(Error, Debug)]
 pub enum TxRuntimeError {
     #[error("Out of gas: {0}")]
```

### crates/sdk/src/rpc.rs
```diff
@@ -818,7 +818,7 @@ pub async fn get_delegators_delegation<C: crate::queries::Client + Sync>(
     )
 }
 
-/// Get the delegator's delegation at some epoh
+/// Get the delegator's delegation at some epoch
 pub async fn get_delegators_delegation_at<C: crate::queries::Client + Sync>(
     client: &C,
     address: &Address,
```
