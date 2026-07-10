### Title
Byzantine Leader Participant-List Injection in Key Resharing — (`crates/node/src/providers/ecdsa/key_resharing.rs`, `crates/node/src/key_events.rs`)

---

### Summary

`KeyResharingComputation::compute` derives `new_participants` exclusively from `channel.participants()`, which is populated verbatim from the leader's `MpcStartMessage`. Follower nodes never cross-check this list against the contract's `proposed_parameters`. A Byzantine leader can therefore inject an arbitrary participant set into the resharing protocol, causing keyshares to be bound to a set that diverges from the on-chain state.

---

### Finding Description

**Root cause — no follower-side validation of the channel participant list:**

In `KeyResharingComputation::compute` (identical across ECDSA, EdDSA, and CKD providers):

```rust
let new_participants = channel
    .participants()   // ← taken verbatim from the leader's MpcStartMessage
    .iter()
    .copied()
    .map(Participant::from)
    .collect::<Vec<_>>();
...
threshold_signatures::reshare::<Secp256K1Sha256, _, _, _>(
    &old_participants,
    self.old_threshold,
    self.my_share,
    self.public_key,
    &new_participants,   // ← fed directly to the cryptographic protocol
    self.threshold,
    me.into(),
    OsRng,
)?;
``` [1](#0-0) 

`channel.participants()` returns `self.sender.participants`, which is set from `start.participants.clone()` when the follower processes the leader's `MpcStartMessage`:

```rust
let channel = NetworkTaskChannel {
    sender: Arc::new(NetworkTaskChannelSender {
        ...
        participants: start.participants.clone(),   // ← leader-supplied, unverified
        ...
    }),
    ...
};
``` [2](#0-1) 

**Leader constructs the participant list from `all_participant_ids()`:**

```rust
let participants = client.all_participant_ids();
let channel = match client.new_channel_for_task(
    EcdsaTaskId::KeyResharing { key_event: key_event_id },
    participants,   // ← Byzantine leader substitutes a manipulated list here
) {
``` [3](#0-2) 

`all_participant_ids()` delegates to `transport_sender.all_participant_ids()`, which is initialized from `mpc_config.participants` (the contract's new participant set). A Byzantine leader replaces this call with a manipulated list before passing it to `new_channel_for_task`.

**Follower accepts the channel without contract-state verification:**

```rust
pub async fn resharing_follower(...) {
    loop {
        let channel = channel_receiver.recv().await...;
        let key_event_id = match channel.task_id() {
            EcdsaTaskId::KeyResharing { key_event } => key_event,
            ...
        };
        // No check: channel.participants() vs contract's proposed_parameters
        tasks.spawn_checked(..., resharing_computation(..., channel, ...));
    }
}
``` [4](#0-3) 

**`vote_reshared` carries no participant-set commitment:**

```rust
chain_txn_sender.send(ChainSendTransactionRequest::VoteReshared(
    contract_args::VoteResharedArgs::new(key_id),   // only key_id, no participant list
)).await?;
``` [5](#0-4) 

The contract cannot detect that the resharing was performed under a different participant set.

---

### Impact Explanation

**Concrete scenario** (n=4, t=3, new joiner D):

1. Byzantine leader (A) calls `new_channel_for_task` with `participants = [A, B, C]` (omitting new joiner D).
2. The `MpcStartMessage` is sent only to B and C; D receives nothing.
3. B and C each receive a channel with `participants = [A, B, C]`. Since each is present in the list, `assert_reshare_keys_invariants` passes. Both complete the resharing under the {A,B,C} Lagrange basis and vote `vote_reshared`.
4. D times out, votes `vote_abort_key_event_instance`.
5. Three `vote_reshared` votes reach the threshold; the contract transitions to Running with epoch participants {A,B,C,D}.
6. D has no valid keyshare for the new epoch. Any signing attempt that selects D fails. D is permanently excluded from the new epoch's signing capability despite being listed as an authorized participant in the contract.

The keyshares held by A, B, C are bound to the {A,B,C} Lagrange basis, not the {A,B,C,D} basis the contract authorized. Signing still works among A, B, C, but the contract's participant-state invariant is permanently broken: the on-chain Running state asserts D is a participant, yet D holds no usable keyshare. [6](#0-5) 

---

### Likelihood Explanation

- Requires controlling exactly one node — the one with the lowest `ParticipantId` (`is_leader_for_key_event` returns true for the minimum ID). [7](#0-6) 
- One Byzantine node is strictly below the signing threshold; no collusion is required.
- The attack is deterministic and requires no timing luck: the leader simply passes a modified participant slice to `new_channel_for_task`.
- `leader_waits_for_success` returns `false`, so the leader does not need followers to confirm before voting reshared. [8](#0-7) 

---

### Recommendation

In `resharing_follower` (and equivalently in `keygen_follower`), after receiving a channel, verify that `channel.participants()` matches the contract's current proposed participant set before spawning the computation:

```rust
let contract_participants = /* derive from key_event_receiver */;
let channel_participants: BTreeSet<_> = channel.participants().iter().copied().collect();
anyhow::ensure!(
    channel_participants == contract_participants,
    "Channel participant list does not match contract's proposed parameters"
);
```

This check should be performed against the `ContractKeyEventInstance` already available via `key_event_receiver`, which is derived from the on-chain state and is not under the leader's control. [4](#0-3) 

---

### Proof of Concept

Using `run_test_clients`, configure 4 participants (A=leader, B, C, D=new joiner). Override the leader's `new_channel_for_task` call to pass `[A, B, C]` instead of `[A, B, C, D]`. Assert:

1. B and C complete resharing and produce `KeygenOutput` with `public_key == original_public_key` (the public key is preserved — the only existing check passes).
2. D's resharing fails with `MissingParticipant`.
3. A, B, C's keyshares are bound to the {A,B,C} Lagrange basis.
4. A signing attempt using D's (absent) keyshare fails, while a signing attempt using only {A,B,C} succeeds.
5. The contract-side invariant — that all four participants hold valid keyshares — is violated.

### Citations

**File:** crates/node/src/providers/ecdsa/key_resharing.rs (L60-85)
```rust
    async fn compute(self, channel: &mut NetworkTaskChannel) -> anyhow::Result<KeygenOutput> {
        let me = channel.my_participant_id();
        let new_participants = channel
            .participants()
            .iter()
            .copied()
            .map(Participant::from)
            .collect::<Vec<_>>();

        let old_participants = self
            .old_participants
            .into_iter()
            .map(Participant::from)
            .collect::<Vec<_>>();

        let protocol = threshold_signatures::reshare::<Secp256K1Sha256, _, _, _>(
            &old_participants,
            self.old_threshold,
            self.my_share,
            self.public_key,
            &new_participants,
            self.threshold,
            me.into(),
            OsRng,
        )?;
        run_protocol("ecdsa key resharing", channel, protocol).await
```

**File:** crates/node/src/providers/ecdsa/key_resharing.rs (L87-90)
```rust
    fn leader_waits_for_success(&self) -> bool {
        false
    }
}
```

**File:** crates/node/src/network.rs (L306-330)
```rust
                let channel = NetworkTaskChannel {
                    sender: Arc::new(NetworkTaskChannelSender {
                        channel_id,
                        task_id: start.task_id,
                        leader: originator,
                        my_participant_id: self.my_participant_id(),
                        participants: start.participants.clone(),
                        connection_versions: start
                            .participants
                            .iter()
                            .filter(|id| **id != self.my_participant_id())
                            .map(|id| {
                                (
                                    *id,
                                    self.transport_sender.connectivity(*id).connection_version(),
                                )
                            })
                            .collect(),
                        transport_sender: self.transport_sender.clone(),
                    }),
                    successful_participants: HashSet::new(),
                    receiver: incomplete_channel.receiver,
                    drop: Some(Box::new(drop_fn)),
                };
                return SenderOrNewChannel::NewChannel(channel);
```

**File:** crates/node/src/key_events.rs (L310-314)
```rust
    chain_txn_sender
        .send(ChainSendTransactionRequest::VoteReshared(
            contract_args::VoteResharedArgs::new(key_id),
        ))
        .await?;
```

**File:** crates/node/src/key_events.rs (L593-605)
```rust
        let participants = client.all_participant_ids();
        let channel = match client.new_channel_for_task(
            EcdsaTaskId::KeyResharing {
                key_event: key_event_id,
            },
            participants,
        ) {
            Ok(channel) => channel,
            Err(err) => {
                tracing::warn!(error =%err, "Failed to create channel for resharing computation; retrying.");
                continue;
            }
        };
```

**File:** crates/node/src/key_events.rs (L628-665)
```rust
pub async fn resharing_follower(
    mut channel_receiver: mpsc::UnboundedReceiver<NetworkTaskChannel>,
    keyshare_storage: Arc<RwLock<KeyshareStorage>>,
    key_event_receiver: watch::Receiver<ContractKeyEventInstance>,
    chain_txn_sender: impl TransactionSender + 'static,
    args: Arc<ResharingArgs>,
) -> anyhow::Result<()> {
    let mut tasks = AutoAbortTaskCollection::new();
    loop {
        let channel = channel_receiver
            .recv()
            .await
            .ok_or_else(|| anyhow::anyhow!("Channel receiver closed unexpectedly; exiting."))?;
        let key_event_id = match channel.task_id() {
            crate::primitives::MpcTaskId::EcdsaTaskId(EcdsaTaskId::KeyResharing { key_event }) => {
                key_event
            }
            crate::primitives::MpcTaskId::EddsaTaskId(EddsaTaskId::KeyResharing { key_event }) => {
                key_event
            }
            _ => {
                tracing::info!("Ignoring non-resharing task {:?}", channel.task_id());
                continue;
            }
        };

        tasks.spawn_checked(
            &format!("key resharing follower for {:?}", key_event_id),
            resharing_computation(
                key_event_receiver.clone(),
                channel,
                keyshare_storage.clone(),
                chain_txn_sender.clone(),
                key_event_id,
                args.clone(),
            ),
        );
    }
```

**File:** crates/node/src/coordinator.rs (L778-804)
```rust
        let new_threshold: usize = mpc_config.participants.threshold.try_into()?;
        let args = Arc::new(ResharingArgs {
            previous_keyset,
            existing_keyshares,
            new_threshold: TSReconstructionThreshold::from(new_threshold),
            old_participants: current_running_state.participants,
        });

        if mpc_config.is_leader_for_key_event() {
            resharing_leader(
                network_client,
                keyshare_storage,
                key_event_receiver,
                chain_txn_sender,
                args,
            )
            .await?;
        } else {
            resharing_follower(
                channel_receiver,
                keyshare_storage,
                key_event_receiver,
                chain_txn_sender,
                args,
            )
            .await?;
        }
```

**File:** crates/node/src/config.rs (L49-59)
```rust
    pub fn is_leader_for_key_event(&self) -> bool {
        let my_participant_id = self.my_participant_id;
        let participant_with_lowest_id = self
            .participants
            .participants
            .iter()
            .map(|p| p.id)
            .min()
            .expect("Participants list should not be empty");
        my_participant_id == participant_with_lowest_id
    }
```
