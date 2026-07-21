### Title
Vote Identity Field (`voter`) Never Validated Against Cryptographic Signature in Consensus — (`File: crates/apollo_consensus/src/single_height_consensus.rs`)

### Summary

The `handle_vote` function in the Apollo consensus engine accepts any `Vote` message whose `voter` field names a committee member, without ever verifying that the attached `signature` was produced by the private key corresponding to that `voter` address. This is the direct sequencer analog of the RaptorCast identity-field impersonation bug: the identity claim in the message payload is never bound to the cryptographic proof of origin.

### Finding Description

The `Vote` struct carries two relevant fields:

```rust
pub struct Vote {
    ...
    pub voter: ContractAddress,   // identity claim
    pub signature: RawSignature,  // cryptographic proof — never checked
}
``` [1](#0-0) 

The self-vote path in the state machine explicitly defers signing:

```rust
// TODO(Asmaa): sign the vote
signature: RawSignature::default(),
``` [2](#0-1) 

The incoming-vote handler explicitly defers verification:

```rust
pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
    // TODO(Asmaa): verify the signature
    ...
    if !self.committee.members().iter().any(|s| s.address == vote.voter) {
        debug!("Ignoring vote from non validator: vote={:?}", vote);
        return VecDeque::new();
    }
    // proceeds to feed vote into state machine
``` [3](#0-2) 

The only guard is a committee-membership check on the **claimed** `vote.voter` address. There is no step that recovers or verifies the public key from `vote.signature` and compares it to the staker's registered key. The `Staker` struct does carry a `public_key: Felt` field for exactly this purpose, but it is never consulted during vote processing: [4](#0-3) 

The codebase itself acknowledges the gap in the future-vote cache comment:

> "Since vote signatures are not yet verified, a peer can forge votes with arbitrary voter addresses; without this cap that would grow `future_votes` without bound and exhaust memory." [5](#0-4) 

The signing infrastructure (`SignatureManager`, `verify_precommit_vote_signature`) exists and is tested, but is never wired into the vote-handling path: [6](#0-5) 

### Impact Explanation

An attacker who can connect to the consensus gossip topic (the same open port used by all peers) can:

1. **Forge prevotes/precommits from any committee member** — craft a `Vote` with `voter = victim_validator_address`, attach any (or a default/zero) `signature`, and broadcast it. The node accepts it as a legitimate vote from that validator.

2. **Manufacture a false quorum** — by forging votes from validators whose combined `StakingWeight` exceeds 2/3 of the total, the attacker causes the local node to reach `DecisionReached` for a `proposal_commitment` without genuine 2/3+ validator agreement. The node then calls `context.decision_reached` and attempts to commit the block, breaking the Byzantine fault-tolerance safety guarantee.

3. **Cause a stuck/crashed node** — if the forged votes name a `proposal_commitment` that the local node never validated (i.e., it is not in `valid_proposals`), the commit lookup fails and the node is left in an inconsistent state.

4. **Liveness attack** — forge NIL precommit votes from enough validators to prevent a legitimate quorum from forming, forcing repeated round changes.

The `proposal_commitment` value is observable on the network (it is broadcast in `ProposalFin`), so an attacker can trivially forge votes for the correct commitment of the current round, causing the node to commit a block without genuine consensus.

### Likelihood Explanation

- The consensus gossip topic is open to any peer that can connect to the node's network port.
- No stake, no registration, and no cost is required — only the ability to send a protobuf-encoded `Vote` message.
- The attack is stateless and repeatable every round.
- The code explicitly marks the missing check as a TODO, confirming it is a known gap rather than an intentional design.

### Recommendation

Wire `verify_precommit_vote_signature` (already implemented in `apollo_signature_manager`) into `handle_vote`. For each incoming vote:

1. Look up the staker's registered `public_key` from the committee by matching `vote.voter`.
2. Call `verify_precommit_vote_signature(block_hash_from_commitment, vote.signature, staker.public_key)`.
3. Reject the vote if verification fails or if the public key is not found.

The signing side (`make_self_vote`) must also be completed to produce a real signature instead of `RawSignature::default()`.

### Proof of Concept

```
1. Attacker connects to the consensus gossip topic (votes_topic).
2. Observes a ProposalFin for height H, round R with commitment C.
3. Selects victim_validator = any ContractAddress in the committee with weight W.
4. Constructs:
     Vote {
         vote_type: Precommit,
         height: H,
         round: R,
         proposal_commitment: Some(C),
         voter: victim_validator,   // identity claim — not the attacker's key
         signature: RawSignature::default(),  // zero / garbage
     }
5. Broadcasts the forged Vote.
6. handle_vote checks: victim_validator ∈ committee → true. Signature check: SKIPPED.
7. State machine records the vote with weight W.
8. Repeat for enough validators to reach 2/3+ weight.
9. Node emits DecisionReached(C) without genuine validator agreement.
```

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L53-61)
```rust
#[derive(Debug, Default, Hash, Clone, Eq, PartialEq, Serialize, Deserialize)]
pub struct Vote {
    pub vote_type: VoteType,
    pub height: BlockNumber,
    pub round: Round,
    pub proposal_commitment: Option<ProposalCommitment>,
    pub voter: ContractAddress,
    pub signature: RawSignature,
}
```

**File:** crates/apollo_consensus/src/state_machine.rs (L254-256)
```rust
            // TODO(Asmaa): sign the vote
            signature: RawSignature::default(),
        };
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

**File:** crates/apollo_staking/src/committee_provider.rs (L24-32)
```rust
pub struct Staker {
    // A contract address of the staker, to which rewards are sent.
    pub address: ContractAddress,
    // The staker's weight, which determines the staker's influence in the consensus (its voting
    // power).
    pub weight: StakingWeight,
    // The public key of the staker, used to verify the staker's identity.
    pub public_key: Felt,
}
```

**File:** crates/apollo_consensus/src/manager.rs (L327-335)
```rust
            // Bound the cache to what an honest committee could produce. Since vote signatures are
            // not yet verified, a peer can forge votes with arbitrary voter addresses; without this
            // cap that would grow `future_votes` without bound and exhaust memory.
            if votes.len() < cap {
                votes.push(vote);
            } else {
                // TODO(Matan): once the network expands beyond the current trusted set, rate-limit
                // this log (e.g. `trace_every_n_ms!`) so that dropping votes can't itself be used
                // as a log-flood DoS.
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
