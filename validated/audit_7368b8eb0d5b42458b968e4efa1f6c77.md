### Title
Single Participant Can Indefinitely Abort Key Generation or Resharing Instances - (`crates/contract/src/state/key_event.rs`)

### Summary

A single attested participant can call `vote_abort_key_event_instance` to immediately destroy the current key event instance without any threshold requirement. Because a new instance must be started by the leader after each abort, a single malicious participant can repeat this indefinitely, permanently preventing key generation (DKG) or key resharing from completing.

### Finding Description

The `vote_abort` function in `key_event.rs` immediately nullifies the active key event instance upon a single participant's call:

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    if self.instance.as_ref().unwrap().completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    self.instance = None;   // <-- single-participant abort, no threshold
    Ok(())
}
``` [1](#0-0) 

The on-chain entry point `vote_abort_key_event_instance` only requires the caller to be an attested participant — no threshold vote is needed: [2](#0-1) 

The node legitimately sends this transaction whenever its local MPC computation fails:

```rust
Err(err) => {
    tracing::error!("Key generation attempt {:?} failed: {:?}; sending vote_abort_key_event_instance", key_id, err);
    chain_txn_sender.send(ChainSendTransactionRequest::VoteAbortKeyEventInstance(...)).await?;
},
``` [3](#0-2) 

The same pattern exists for resharing: [4](#0-3) 

A malicious participant simply modifies their node to always emit `VoteAbortKeyEventInstance` instead of `VotePk` / `VoteReshared`, regardless of whether the local computation actually succeeded.

### Impact Explanation

- **Initializing state (DKG):** The network can never produce a key and never transition to `Running`. All user `sign()` calls are permanently blocked. This is equivalent to permanent freezing of the MPC network's signing capability.
- **Resharing state:** The network can never complete a participant set change. The old key set remains in use indefinitely, blocking governance transitions.

In both cases a single participant — strictly below the signing threshold — can sustain the attack forever by aborting each new instance the leader starts. This matches the "permanent freezing of funds / signing capability" critical impact and the "participant-state manipulation that breaks production safety invariants" medium impact.

### Likelihood Explanation

Any registered, attested participant can execute this attack by modifying their node binary. No external resources, leaked keys, or threshold collusion are required. The attack is cheap (one NEAR transaction per instance) and repeatable with no cost to the attacker beyond staying registered.

### Recommendation

Require a threshold of abort votes before nullifying a key event instance, analogous to how `vote_cancel_keygen` requires threshold votes before cancelling key generation entirely: [5](#0-4) 

Alternatively, replace the single-participant abort with a timeout-only recovery path: if a participant's local computation fails, they simply do nothing and the instance expires naturally after `key_event_timeout_blocks`. This removes the abort shortcut that a malicious participant can exploit.

### Proof of Concept

1. Attested participant `P_malicious` modifies their node to always call `vote_abort_key_event_instance(key_event_id)` immediately upon receiving a new key event ID, instead of running the DKG/resharing protocol.
2. The leader calls `start_keygen_instance` → contract creates instance with `attempt_id = 0`.
3. `P_malicious` submits `vote_abort_key_event_instance({epoch, domain, attempt=0})` → `self.instance = None`.
4. Leader calls `start_keygen_instance` again → `attempt_id = 1`.
5. `P_malicious` aborts again. Steps 4–5 repeat indefinitely.
6. The contract never reaches the state where all participants have submitted `vote_pk`, so no key is ever generated and the network never enters `Running` state. [6](#0-5) [7](#0-6)

### Citations

**File:** crates/contract/src/state/key_event.rs (L143-158)
```rust
    /// Casts a vote to abort the current keygen instance.
    /// A new instance needs to be started later to start a new keygen attempt.
    pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        let candidate = self.verify_vote(&key_event_id)?;
        if self
            .instance
            .as_ref()
            .unwrap()
            .completed
            .contains(&candidate)
        {
            return Err(VoteError::VoteAlreadySubmitted.into());
        }
        self.instance = None;
        Ok(())
    }
```

**File:** crates/contract/src/lib.rs (L1282-1295)
```rust
    /// Casts a vote to abort the current key event instance. If succesful, the contract aborts the
    /// instance and a new instance with the next attempt_id can be started.
    #[handle_result]
    pub fn vote_abort_key_event_instance(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
        log!(
            "vote_abort_key_event_instance: signer={}",
            env::signer_account_id()
        );

        self.assert_caller_is_attested_participant_and_protocol_active();

        self.protocol_state
            .vote_abort_key_event_instance(key_event_id)
    }
```

**File:** crates/node/src/key_events.rs (L111-148)
```rust
/// Wrapper around `keygen_computation_inner` which
///  - Waits for the key event to start.
///  - Interrupts the inner computation if the key event expires.
///  - Sends a `vote_abort_key_event_instance` transaction if the inner computation fails.
async fn keygen_computation(
    mut contract_key_event_id: watch::Receiver<ContractKeyEventInstance>,
    channel: NetworkTaskChannel,
    keyshare_storage: Arc<RwLock<KeyshareStorage>>,
    chain_txn_sender: impl TransactionSender,
    key_id: KeyEventId,
    threshold: ReconstructionThreshold,
) -> anyhow::Result<()> {
    let key_event = wait_for_contract_catchup(&mut contract_key_event_id, key_id).await;
    let inner = keygen_computation_inner(
        channel,
        keyshare_storage,
        chain_txn_sender.clone(),
        key_event.completed_domains,
        key_id,
        key_event.domain,
        threshold,
    );
    let expiration = key_event_id_expiration(contract_key_event_id, key_id);
    tokio::select! {
        res = inner => {
            match res {
                Ok(()) => {
                    tracing::info!("Key generation attempt {:?} completed successfully.", key_id);
                },
                Err(err) => {
                    tracing::error!("Key generation attempt {:?} failed: {:?}; sending vote_abort_key_event_instance", key_id, err);
                    chain_txn_sender.send(ChainSendTransactionRequest::VoteAbortKeyEventInstance(contract_args::VoteAbortKeyEventInstanceArgs::new(key_id))).await?;
                },
            }
        },
        _ = expiration => anyhow::bail!("Key event expired before computation completed."),
    }
    Ok(())
```

**File:** crates/node/src/key_events.rs (L346-350)
```rust
                },
                Err(err) => {
                    tracing::error!("Key resharing attempt {:?} failed: {:?}; sending vote_abort_key_event_instance", key_id, err);
                    chain_txn_sender.send(ChainSendTransactionRequest::VoteAbortKeyEventInstance(contract_args::VoteAbortKeyEventInstanceArgs::new(key_id))).await?;
                },
```

**File:** crates/contract/src/state/initializing.rs (L117-142)
```rust
    pub fn vote_cancel(
        &mut self,
        next_domain_id: u64,
    ) -> Result<Option<RunningContractState>, Error> {
        if next_domain_id != self.domains.next_domain_id() {
            return Err(InvalidParameters::NextDomainIdMismatch.into());
        }
        let participant = AuthenticatedParticipantId::new(
            self.generating_key.proposed_parameters().participants(),
        )?;
        let required_threshold = self
            .generating_key
            .proposed_parameters()
            .threshold()
            .value() as usize;
        if self.cancel_votes.insert(participant) && self.cancel_votes.len() >= required_threshold {
            let mut domains = self.domains.clone();
            domains.retain_domains(self.generated_keys.len());
            return Ok(Some(RunningContractState::new(
                domains,
                Keyset::new(self.epoch_id, self.generated_keys.clone()),
                self.generating_key.proposed_parameters().clone(),
                AddDomainsVotes::default(),
            )));
        }
        Ok(None)
```
