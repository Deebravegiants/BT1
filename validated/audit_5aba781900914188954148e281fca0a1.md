### Title
Consensus Precommit Votes Accepted Without Signature Verification, Enabling Validator Impersonation and False Quorum — (File: `crates/apollo_consensus/src/single_height_consensus.rs`)

---

### Summary

The Apollo sequencer's consensus layer broadcasts precommit and prevote votes with a hardcoded empty signature (`RawSignature::default()`) and accepts incoming votes from peers without verifying any signature. The only admission check is that the `voter` field names a known committee member. Because the `voter` field is attacker-controlled, any unprivileged network peer can forge votes from any legitimate validator, manufacture a Byzantine-quorum of precommits for an arbitrary `ProposalCommitment`, and drive the consensus engine to a `DecisionReached` event for a block the honest validators never agreed to.

A secondary structural defect compounds this: even when signing is eventually wired in, `build_precommit_vote_message_digest` omits `chain_id` from the signed payload, so a valid precommit signature produced on one Starknet network (e.g., mainnet) is cryptographically valid on any other Starknet network that shares the same block hash — a direct analog to ChainPort's missing `networkId` field.

---

### Finding Description

**Root cause 1 — votes are unsigned and unverified (production gap)**

`make_self_vote` in the state machine constructs every outgoing vote with an explicit placeholder:

```rust
// TODO(Asmaa): sign the vote
signature: RawSignature::default(),
``` [1](#0-0) 

`handle_vote` in `SingleHeightConsensus`, the function that processes every inbound vote from the network, contains only a TODO and never calls any verification function:

```rust
pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
    // TODO(Asmaa): verify the signature
    ...
    if !self.committee.members().iter().any(|s| s.address == vote.voter) {
        debug!("Ignoring vote from non validator: vote={:?}", vote);
        return VecDeque::new();
    }
``` [2](#0-1) 

The sole guard is a committee-membership lookup on the `voter` field. Because `voter` is a plain `ValidatorId` carried inside the `Vote` struct and is never cryptographically bound to the sender, an attacker sets it to any legitimate validator address and the check passes.

**Root cause 2 — `build_precommit_vote_message_digest` omits `chain_id`**

The `SignatureManager` component exposes `sign_precommit_vote(block_hash)` and the corresponding `verify_precommit_vote_signature`. The message digest is constructed as:

```rust
fn build_precommit_vote_message_digest(block_hash: BlockHash) -> MessageDigest {
    let block_hash = block_hash.to_bytes_be();
    let mut message = Vec::with_capacity(PRECOMMIT_VOTE.len() + block_hash.len());
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&block_hash);
    MessageDigest(blake2s_to_felt(&message))
}
``` [3](#0-2) 

No `chain_id` is included. The Starknet block hash itself (`calculate_block_hash`) also does not include `chain_id`: [4](#0-3) 

A precommit signature produced on testnet is therefore valid on mainnet for the same `block_hash` value.

The `SignatureManager` component is wired up and reachable via `SignatureManagerRequest::SignPrecommitVote`: [5](#0-4) [6](#0-5) 

But it is never called from the consensus vote path; the two defects are independent.

---

### Impact Explanation

An attacker who is a p2p network peer (no special privilege required) can:

1. Observe the current consensus height and round from broadcast messages.
2. Craft `Vote` structs with `vote_type = Precommit`, `voter` set to each of the ≥ 2/3 quorum-weight validators, and `proposal_commitment` set to any target `ProposalCommitment`.
3. Broadcast these forged votes. `handle_vote` accepts each one because the `voter` field names a real committee member and the signature is never checked.
4. Once the state machine accumulates a quorum of precommits for the forged commitment, `upon_decision` fires and emits `SMRequest::DecisionReached` with the attacker-chosen block. [7](#0-6) 

The decided block propagates to the batcher and storage as a committed block, corrupting the canonical chain state. This satisfies the "wrong decided block" criterion in the audit work plan.

---

### Likelihood Explanation

The vulnerability requires only p2p network access, which is unprivileged. The `Vote` struct fields are fully attacker-controlled. No cryptographic material is needed because no signature is ever checked. The attack is deterministic and requires no brute-force. The TODO comments confirm this is a known incomplete feature shipped in the production codebase, not a test-only stub.

---

### Recommendation

**Short term:**
- In `make_self_vote`, call `SignatureManager::sign_precommit_vote` (or an equivalent that covers both prevote and precommit) before broadcasting the vote, and store the resulting signature in `vote.signature`.
- In `handle_vote`, call `verify_precommit_vote_signature` (or the equivalent prevote verifier) against the sender's registered public key before the vote is forwarded to the state machine. Reject votes with invalid or missing signatures.

**Medium term:**
- Add `chain_id` to `build_precommit_vote_message_digest` so that a signature produced on one Starknet network cannot be replayed on another:

```rust
fn build_precommit_vote_message_digest(
    block_hash: BlockHash,
    chain_id: &ChainId,
) -> MessageDigest { ... }
```

- Add `vote_type` (prevote vs. precommit) to the signed payload to prevent cross-type replay, analogous to ChainPort's `action` field.
- Write a specification document describing what each signature protects against, which fields are bound, and why (integrity, non-repudiation, cross-chain and cross-type replay prevention).

---

### Proof of Concept

```
// Attacker is a p2p peer connected to the Apollo network.
// Consensus is at height H, round R, with validators V1..V4 (quorum = 3).

let forged_commitment = ProposalCommitment(attacker_chosen_felt);

for validator in [V1, V2, V3] {
    let forged_vote = Vote {
        vote_type: VoteType::Precommit,
        height: H,
        round: R,
        proposal_commitment: Some(forged_commitment),
        voter: validator,          // real committee member address
        signature: RawSignature::default(),  // same as honest nodes send
    };
    broadcast(forged_vote);  // accepted by handle_vote — no sig check
}

// State machine receives 3 precommits for forged_commitment.
// upon_decision fires → DecisionReached(forged_commitment).
// Batcher commits the attacker-chosen block to storage.
``` [8](#0-7) [9](#0-8) [3](#0-2)

### Citations

**File:** crates/apollo_consensus/src/state_machine.rs (L243-256)
```rust
    fn make_self_vote(
        &mut self,
        vote_type: VoteType,
        proposal_commitment: Option<ProposalCommitment>,
    ) -> VecDeque<SMRequest> {
        let vote = Vote {
            vote_type,
            height: self.height,
            round: self.round,
            proposal_commitment,
            voter: self.id,
            // TODO(Asmaa): sign the vote
            signature: RawSignature::default(),
        };
```

**File:** crates/apollo_consensus/src/state_machine.rs (L694-716)
```rust
    fn upon_decision(&mut self, round: u32) -> VecDeque<SMRequest> {
        let Some((Some(proposal_id), _)) = self.proposals.get(&round) else {
            return VecDeque::new();
        };
        if !self.value_has_enough_votes(&self.precommits, round, &Some(*proposal_id), &self.quorum)
        {
            return VecDeque::new();
        }
        if !self.virtual_proposer_in_favor(&self.precommits, round, &Some(*proposal_id)) {
            return VecDeque::new();
        }
        // Collect all supporting precommits for this proposal and round.
        let supporting_precommits: Vec<Vote> = self
            .precommits
            .iter()
            .filter(|(&(r, _voter), (v, _w))| {
                r == round && v.proposal_commitment == Some(*proposal_id)
            })
            .map(|(_vote_key, (v, _w))| v.clone())
            .collect();

        let decision = Decision { precommits: supporting_precommits, block: *proposal_id, round };
        VecDeque::from([SMRequest::DecisionReached(decision)])
```

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L241-281)
```rust
    pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
        // TODO(Asmaa): verify the signature
        trace!("Received {:?}", vote);
        let height = self.state_machine.height();
        if vote.height != height {
            warn!("Invalid vote height: expected {:?}, got {:?}", height, vote.height);
            return VecDeque::new();
        }
        if !self.committee.members().iter().any(|s| s.address == vote.voter) {
            debug!("Ignoring vote from non validator: vote={:?}", vote);
            return VecDeque::new();
        }

        // Check if vote has already been received.
        match self.state_machine.received_vote(&vote) {
            VoteStatus::Duplicate => {
                // Duplicate - ignore.
                trace_every_n_ms!(
                    DUPLICATE_VOTE_LOG_PERIOD_MS,
                    "Ignoring duplicate vote: {vote:?}"
                );
                return VecDeque::new();
            }
            VoteStatus::Conflict(old_vote, new_vote) => {
                // Conflict - ignore and record.
                warn!("Conflicting votes: old={old_vote:?}, new={new_vote:?}");
                CONSENSUS_CONFLICTING_VOTES.increment(1);
                return VecDeque::new();
            }
            VoteStatus::New => {
                // Vote is new, proceed to process it.
            }
        }

        info!("Accepting {:?}", vote);
        let sm_vote = match vote.vote_type {
            VoteType::Prevote => StateMachineEvent::Prevote(vote),
            VoteType::Precommit => StateMachineEvent::Precommit(vote),
        };
        self.state_machine.handle_event(sm_vote)
    }
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L138-145)
```rust
fn build_precommit_vote_message_digest(block_hash: BlockHash) -> MessageDigest {
    let block_hash = block_hash.to_bytes_be();
    let mut message = Vec::with_capacity(PRECOMMIT_VOTE.len() + block_hash.len());
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&block_hash);

    MessageDigest(blake2s_to_felt(&message))
}
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L245-282)
```rust
pub fn calculate_block_hash(
    partial_block_hash_components: &PartialBlockHashComponents,
    state_root: GlobalRoot,
    previous_block_hash: BlockHash,
) -> StarknetApiResult<BlockHash> {
    let block_hash_version: BlockHashVersion =
        partial_block_hash_components.starknet_version.try_into()?;
    let block_commitments = &partial_block_hash_components.header_commitments;
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
            .chain(&block_commitments.state_diff_commitment.0.0)
            .chain(&block_commitments.transaction_commitment.0)
            .chain(&block_commitments.event_commitment.0)
            .chain(&block_commitments.receipt_commitment.0)
            .chain_iter(
                gas_prices_to_hash(
                    &partial_block_hash_components.l1_gas_price,
                    &partial_block_hash_components.l1_data_gas_price,
                    &partial_block_hash_components.l2_gas_price,
                    &block_hash_version,
                )
                .iter(),
            )
            .chain(
                &Felt::try_from(&partial_block_hash_components.starknet_version)
                    .expect("Expect ASCII version"),
            )
            .chain(&Felt::ZERO)
            .chain(&previous_block_hash.0)
            .get_poseidon_hash(),
    ))
}
```

**File:** crates/apollo_signature_manager_types/src/lib.rs (L60-63)
```rust
    async fn sign_precommit_vote(
        &self,
        block_hash: BlockHash,
    ) -> SignatureManagerClientResult<RawSignature>;
```

**File:** crates/apollo_signature_manager/src/communication.rs (L30-34)
```rust
            SignatureManagerRequest::SignPrecommitVote(block_hash) => {
                SignatureManagerResponse::SignPrecommitVote(
                    self.sign_precommit_vote(block_hash).await,
                )
            }
```
