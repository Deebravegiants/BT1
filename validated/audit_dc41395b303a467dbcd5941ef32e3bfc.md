### Title
Missing Vote Signature Verification Allows Any Network Peer to Forge Consensus Votes for Arbitrary Committee Members — (`File: crates/apollo_consensus/src/single_height_consensus.rs`)

### Summary
`handle_vote` in `SingleHeightConsensus` explicitly skips cryptographic signature verification with a `// TODO(Asmaa): verify the signature` comment. The only admission guard is a membership check on the attacker-controlled `vote.voter` field. Any network peer can forge votes claiming to be any committee member with a zero/default signature, potentially driving the consensus state machine to a quorum decision on a wrong block.

### Finding Description
In `crates/apollo_consensus/src/single_height_consensus.rs`, `handle_vote` performs two checks before accepting a vote into the state machine:

1. Height match (`vote.height != height`)
2. Committee membership (`self.committee.members().iter().any(|s| s.address == vote.voter)`) [1](#0-0) 

The signature field (`vote.signature`) is never inspected. The comment at line 242 reads `// TODO(Asmaa): verify the signature`, confirming this is a known, unimplemented guard. The `vote.voter` field is a plain `ContractAddress` that arrives over the wire and is fully attacker-controlled; it is never bound to the network identity of the sender.

The `Vote` struct carries a `RawSignature` field whose `Default` implementation produces an all-zero value: [2](#0-1) 

The cache code itself acknowledges the consequence: *"Since vote signatures are not yet verified, a peer can forge votes with arbitrary voter addresses."* [3](#0-2) 

The direct analog to the external report is:
- **External**: `rfqOrderSigner == address(0)` → `signer == rfqOrderSigner` trivially true → signature check bypassed.
- **Sequencer**: `vote.signature` is never checked → any `vote.voter` that matches a committee address is accepted regardless of signature → committee membership check bypassed cryptographically.

### Impact Explanation
A single unprivileged network peer can:
1. Read the public committee member addresses (they are part of the consensus configuration).
2. Emit `n` forged `Vote` messages, each with `vote.voter` set to a different committee member's address and `vote.signature` set to the zero default.
3. Because `handle_vote` accepts every such vote, the attacker injects `n` votes into the state machine — one per committee member — without holding any private key.
4. With enough forged votes the state machine reaches a prevote or precommit quorum for an attacker-chosen `proposal_commitment`, causing `SMRequest::DecisionReached` to fire for a wrong block. [4](#0-3) 

A wrong `DecisionReached` propagates to `decision_reached` in the orchestrator, which calls `batcher.decision_reached` and `state_sync_client.add_new_block`, committing a wrong block and producing a wrong state root, wrong receipts, and wrong event commitments.

### Likelihood Explanation
- The committee addresses are not secret; they are broadcast as part of consensus configuration.
- No network-layer authentication binds `vote.voter` to the TCP/libp2p identity of the sender.
- The attacker needs only a single P2P connection to the sequencer node.
- The `RawSignature::default()` (all-zero) value is the natural payload for a forged vote and passes the absent check trivially.
- The cache comment explicitly acknowledges the attack surface exists today.

### Recommendation
1. **Implement signature verification in `handle_vote`** before the committee membership check. Use `verify_precommit_vote_signature` / `verify_identity` from `apollo_signature_manager` with the committee member's registered public key. [5](#0-4) 

2. **Reject votes with a zero/default signature** as an additional guard, mirroring the recommendation in the external report.
3. **Store each committee member's public key** alongside their address in the `Committee` struct so the verifier can look it up by `vote.voter`.
4. **Add a test** that sends a vote with a valid `voter` address but an invalid signature and asserts it is rejected.

### Proof of Concept
```
Attacker (single P2P peer):

for each validator_address in committee.members():
    vote = Vote {
        vote_type:           VoteType::Precommit,
        height:              current_height,
        round:               current_round,
        proposal_commitment: Some(attacker_chosen_commitment),
        voter:               validator_address,   // attacker-controlled field
        signature:           RawSignature::default(),  // all-zero, never checked
    }
    broadcast(vote)

// handle_vote accepts every vote because:
//   1. vote.height == current_height  ✓
//   2. committee.members().any(|s| s.address == vote.voter)  ✓  (address is public)
//   3. signature check: // TODO(Asmaa): verify the signature  ← SKIPPED

// After n votes (≥ quorum threshold), state machine fires:
//   SMRequest::DecisionReached { block: attacker_chosen_commitment, ... }
``` [6](#0-5)

### Citations

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

**File:** crates/apollo_consensus/src/test_utils.rs (L133-141)
```rust
    Vote {
        vote_type: VoteType::Prevote,
        height,
        round,
        proposal_commitment,
        voter,
        signature: RawSignature::default(),
    }
}
```

**File:** crates/apollo_consensus/src/manager.rs (L327-330)
```rust
            // Bound the cache to what an honest committee could produce. Since vote signatures are
            // not yet verified, a peer can forge votes with arbitrary voter addresses; without this
            // cap that would grow `future_votes` without bound and exhaust memory.
            if votes.len() < cap {
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

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L179-186)
```rust
pub fn verify_precommit_vote_signature(
    block_hash: BlockHash,
    signature: RawSignature,
    public_key: PublicKey,
) -> SignatureVerificationResult<bool> {
    let message_digest = build_precommit_vote_message_digest(block_hash);
    verify_signature(message_digest, signature, public_key)
}
```
