### Title
Single-Participant Abort Enables Byzantine Node to Permanently Loop Key-Generation/Resharing State Machine — (File: `crates/contract/src/state/key_event.rs`)

---

### Summary

The `vote_abort` function in the MPC contract allows **any single valid participant** to abort an active key-event instance with no threshold requirement. A Byzantine participant strictly below the signing threshold can exploit this to repeatedly abort every key-generation or resharing attempt the moment the leader starts one, trapping the leader node in an infinite retry loop and permanently preventing key setup or participant-set transitions from completing.

---

### Finding Description

**Root cause — `vote_abort` requires no threshold (`key_event.rs` lines 145–158)** [1](#0-0) 

```rust
pub fn vote_abort(&mut self, key_event_id: KeyEventId) -> Result<(), Error> {
    let candidate = self.verify_vote(&key_event_id)?;
    if self.instance.as_ref().unwrap().completed.contains(&candidate) {
        return Err(VoteError::VoteAlreadySubmitted.into());
    }
    self.instance = None   // ← entire instance destroyed by one participant
    Ok(())
}
```

`verify_vote` only checks that the signer is a registered participant; it does **not** require a threshold of abort votes. The sole guard (`completed.contains(&candidate)`) only blocks a participant who already cast a *success* vote — it does not prevent a participant who has not yet voted from aborting unilaterally. [2](#0-1) 

**How the leader node loops — `keygen_leader` / `resharing_leader` (`key_events.rs` lines 402–481, 528–623)**

The leader loop is:

1. Wait for `contract_event.started == false` → read `key_event_id`.
2. Send `StartKeygen` (or `StartReshare`).
3. Wait up to `MAX_LATENCY_BEFORE_EXPECTING_TRANSACTION_TO_FINALIZE` (20 s) for `started == true`.
4. Run `keygen_computation` / `resharing_computation`.
5. On any failure → `continue` back to step 1. [3](#0-2) 

The `keygen_computation` wrapper selects between the inner computation and a `key_event_id_expiration` future. The expiration future resolves as `RemoteAhead` the moment the contract's `next_attempt_id` advances past the current attempt — which happens immediately when `vote_abort` sets `instance = None` (the `next_attempt_id` was already incremented during `start()`). [4](#0-3) [5](#0-4) 

**The loop in detail:**

| Step | Leader node | Byzantine participant |
|------|-------------|----------------------|
| 1 | Sees `started=false`, reads `key_event_id=(e,d,attempt=N)` | — |
| 2 | Sends `StartKeygen(N)` → accepted on-chain | — |
| 3 | Waits for `started=true` | Immediately sends `vote_abort_key_event_instance(N)` → accepted; `instance=None` |
| 4 | `key_event_id_expiration` fires (contract is now `RemoteAhead`); `keygen_computation` returns `Err` | — |
| 5 | Loops back to step 1 with `attempt=N+1` | Repeats abort for `N+1` |

This is structurally identical to the Arbitrum `edgeBisecting → edgeBackToStart → edgeStarted → edgeBisecting` loop described in the reference report: the node cannot detect that the on-chain state was already invalidated by an adversary, so it retries the same failing action indefinitely. [6](#0-5) 

---

### Impact Explanation

**During Initialization (`Initializing` state):** The MPC network can never complete key generation. No signing keys are ever produced, so the network can never issue threshold signatures. This is a permanent freeze of all funds and capabilities controlled by the MPC network — **Critical/High**.

**During Resharing (`Running` state with resharing sub-state):** A participant scheduled for removal can abort every resharing attempt, preventing the new participant set from ever taking effect. The old (compromised) participant set remains in control indefinitely — **High**.

Both impacts are reachable without any threshold collusion: a single Byzantine participant suffices.

---

### Likelihood Explanation

- The attacker must be a registered participant in the current key event — a realistic assumption for a Byzantine node.
- No special privileges, no TEE bypass, no network-level attack required.
- The attack is trivially automated: watch the contract for `started=true`, immediately submit `vote_abort_key_event_instance`.
- The contract exposes no rate-limiting or cooldown on abort votes.

Likelihood: **Medium** (requires one Byzantine participant; straightforward to execute).

---

### Recommendation

Replace the single-participant abort with a **threshold-based abort**: require at least `t` participants to vote abort before the instance is cancelled, mirroring the threshold requirement for success votes. Alternatively, restrict abort votes to the leader only, or introduce a cooldown that prevents the same participant from aborting consecutive instances.

---

### Proof of Concept

```
Setup: 3-of-5 MPC network in Initializing state.
       Participant P_evil is a valid participant (below threshold).

1. Leader sends StartKeygen(key_event_id=(epoch=1, domain=0, attempt=0)).
   Contract: instance = Some(attempt=0), started=true.

2. P_evil submits vote_abort_key_event_instance(key_event_id=(epoch=1, domain=0, attempt=0)).
   Contract: instance = None, started=false.
   [vote_abort succeeds because P_evil has not yet voted success]

3. Leader's key_event_id_expiration future resolves (RemoteAhead).
   keygen_computation returns Err("Key event expired").
   keygen_leader logs warning and loops back.

4. Leader reads new key_event_id=(epoch=1, domain=0, attempt=1).
   Sends StartKeygen(attempt=1).

5. P_evil aborts attempt=1.

6. Repeat indefinitely → key generation never completes.
```

Relevant contract entry point: `vote_abort` in `crates/contract/src/state/key_event.rs` lines 145–158. [1](#0-0) 

Relevant node loop: `keygen_leader` in `crates/node/src/key_events.rs` lines 409–481. [3](#0-2)

### Citations

**File:** crates/contract/src/state/key_event.rs (L63-79)
```rust
    /// Start a new key event instance as the leader, if one isn't already active.
    /// The leader is always the participant with the lowest participant ID.
    pub fn start(&mut self, key_event_id: KeyEventId, timeout_blocks: u64) -> Result<(), Error> {
        self.cleanup_if_timed_out();
        if self.instance.is_some() {
            return Err(KeyEventError::ActiveKeyEvent.into());
        }
        let expected_key_event_id =
            KeyEventId::new(self.epoch_id, self.domain.id, self.next_attempt_id);
        if key_event_id != expected_key_event_id {
            return Err(KeyEventError::KeyEventIdMismatch.into());
        }
        self.verify_leader()?;
        self.instance = Some(KeyEventInstance::new(self.next_attempt_id, timeout_blocks));
        self.next_attempt_id = self.next_attempt_id.next();
        Ok(())
    }
```

**File:** crates/contract/src/state/key_event.rs (L145-158)
```rust
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

**File:** crates/contract/src/state/key_event.rs (L171-189)
```rust
    /// Verifies that the signer is authorized to cast a vote and that the key event ID corresponds
    /// to the current generation attempt.
    fn verify_vote(
        &mut self,
        key_event_id: &KeyEventId,
    ) -> Result<AuthenticatedParticipantId, Error> {
        let candidate = AuthenticatedParticipantId::new(self.parameters.participants())?;
        self.cleanup_if_timed_out();
        let Some(instance) = self.instance.as_ref() else {
            return Err(KeyEventError::NoActiveKeyEvent.into());
        };
        if key_event_id.epoch_id != self.epoch_id
            || key_event_id.domain_id != self.domain.id
            || key_event_id.attempt_id != instance.attempt_id
        {
            return Err(KeyEventError::KeyEventIdMismatch.into());
        }
        Ok(candidate)
    }
```

**File:** crates/node/src/key_events.rs (L133-148)
```rust
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

**File:** crates/node/src/key_events.rs (L379-392)
```rust
async fn key_event_id_expiration(
    mut key_event_receiver: watch::Receiver<ContractKeyEventInstance>,
    key_event_id: KeyEventId,
) {
    key_event_receiver
        .wait_for(|contract_event| {
            matches!(
                contract_event.compare_to_expected_key_event_id(&key_event_id),
                KeyEventIdComparisonResult::RemoteAhead
            )
        })
        .await
        .expect("Should not fail since closure does not panic");
}
```

**File:** crates/node/src/key_events.rs (L409-481)
```rust
    loop {
        // Wait for all participants to be connected. Otherwise, computations are most likely going
        // to fail so don't waste the effort.
        client.wait_for_all_participants_connected().await?;

        // Wait for the contract to have no active key event instance.
        let key_event_id = key_event_receiver
            .wait_for(|contract_event| !contract_event.started)
            .await?
            .id;
        // Send txn to start the keygen instance. This may or may not end up in the chain; we'll
        // wait for it. If it doesn't happen after some time, we try again.
        chain_txn_sender
            .send(ChainSendTransactionRequest::StartKeygen(
                contract_args::StartKeygenArgs::new(key_event_id),
            ))
            .await?;

        match timeout(
            MAX_LATENCY_BEFORE_EXPECTING_TRANSACTION_TO_FINALIZE,
            key_event_receiver.wait_for(|contract_event| contract_event.started),
        )
        .await
        {
            Ok(res) => {
                let contract_key_event_id = res?.id;
                if contract_key_event_id != key_event_id {
                    tracing::warn!(
                        "Activated key event {:?} does not match expected {:?}; retrying.",
                        contract_key_event_id,
                        key_event_id
                    );
                    continue;
                }
            }
            Err(_) => {
                tracing::warn!(
                    "Key event {:?} did not activate in time; retrying.",
                    key_event_id
                );
                continue;
            }
        }

        // Start the keygen computation.
        let participants = client.all_participant_ids();
        let Ok(channel) = client.new_channel_for_task(
            EcdsaTaskId::KeyGeneration {
                key_event: key_event_id,
            },
            participants,
        ) else {
            tracing::warn!("Failed to create channel for keygen computation; retrying.");
            continue;
        };

        if let Err(e) = keygen_computation(
            key_event_receiver.clone(),
            channel,
            keyshare_storage.clone(),
            chain_txn_sender.clone(),
            key_event_id,
            threshold,
        )
        .await
        {
            tracing::warn!(
                "Leader keygen computation {:?} failed, retrying: {:?}",
                key_event_id,
                e
            );
        }
    }
```
