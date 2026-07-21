### Title
Missing Vote Signature Verification Allows Any Network Peer to Forge Consensus Votes — (`File: crates/apollo_consensus/src/single_height_consensus.rs`)

### Summary

`handle_vote()` in `SingleHeightConsensus` accepts consensus votes from any network peer that claims to be a committee member, without ever verifying the cryptographic signature carried in `Vote::signature`. The `verify_precommit_vote_signature` function exists and is wired to the correct ECDSA primitive, but it is never called on the incoming vote path. Any unprivileged P2P peer can forge prevotes or precommits for any committee member address, manufacture a quorum, and drive the node to a `DecisionReached` event for an attacker-chosen `ProposalCommitment`.

---

### Finding Description

The `Vote` struct carries both a `voter: ContractAddress` (the claimed identity) and a `signature: RawSignature` (the ECDSA proof of that identity):

```rust
// crates/apollo_protobuf/src/consensus.rs
pub struct Vote {
    pub vote_type: VoteType,
    pub height: BlockNumber,
    pub round: Round,
    pub proposal_commitment: Option<ProposalCommitment>,
    pub voter: ContractAddress,
    pub signature: RawSignature,   // ← present but never checked
}
``` [1](#0-0) 

`handle_vote()` performs two checks — height equality and committee membership by address — then unconditionally accepts the vote:

```rust
pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
    // TODO(Asmaa): verify the signature          ← acknowledged gap
    ...
    if !self.committee.members().iter().any(|s| s.address == vote.voter) {
        debug!("Ignoring vote from non validator: vote={:?}", vote);
        return VecDeque::new();
    }
    // No signature check; vote is accepted.
    ...
    self.state_machine.handle_event(sm_vote)
}
``` [2](#0-1) 

The committee membership check only validates that `vote.voter` is a known address; it does not verify that the sender actually controls the private key corresponding to that address. The `verify_precommit_vote_signature` function in `apollo_signature_manager` is the intended verification path but is never invoked here:

```rust
pub fn verify_precommit_vote_signature(
    block_hash: BlockHash,
    signature: RawSignature,
    public_key: PublicKey,
) -> SignatureVerificationResult<bool> { ... }
``` [3](#0-2) 

Each `Staker` in the committee carries a `public_key: Felt` that is the intended verification key:

```rust
pub struct Staker {
    pub address: ContractAddress,
    pub weight: StakingWeight,
    pub public_key: Felt,
}
``` [4](#0-3) 

`validate_stakers()` — the only gate before committee construction — checks for duplicate addresses and zero-weight stakers, but **never checks for a zero public key**:

```rust
fn validate_stakers(stakers: StakerSet) -> CommitteeProviderResult<StakerSet> {
    // checks: duplicate address, zero weight, empty set
    // missing: zero public_key check
}
``` [5](#0-4) 

The test utilities confirm that `Felt::ZERO` is a valid public key value that passes all existing guards:

```rust
const STAKER_0: Staker = Staker {
    address: ContractAddress(...),
    weight: StakingWeight(1000),
    public_key: Felt::ZERO,   // passes validate_stakers
};
``` [6](#0-5) 

The test helpers for votes also use `RawSignature::default()` (all-zero), confirming the signature field is structurally present but semantically ignored: [7](#0-6) 

---

### Impact Explanation

An attacker who can send messages on the consensus P2P broadcast channel (any network-connected peer) can:

1. Read the current committee from public state (committee members are public).
2. Craft `Vote` messages with `vote.voter` set to any committee member's `ContractAddress` and `vote.signature` set to arbitrary bytes (or all-zero default).
3. Send enough such forged votes to satisfy the quorum threshold in `value_has_enough_votes`.
4. Trigger `DecisionReached` for an attacker-chosen `ProposalCommitment`, causing the node to commit a block that was never legitimately agreed upon.

This maps to **High** impact: consensus vote signature/hash logic fails to bind the correct signer to the vote, allowing the wrong signer (any peer) to impersonate any committee member.

---

### Likelihood Explanation

- The P2P broadcast channel is reachable by any peer that can establish a libp2p connection. libp2p transport-layer authentication proves the peer's libp2p identity, not its Starknet validator identity.
- Committee member addresses are public (derived from the staking contract).
- The `// TODO(Asmaa): verify the signature` comment confirms the gap is known and not yet closed.
- No other layer in the vote-handling path (`manager.rs` → `handle_vote` → `shc.handle_vote`) performs signature verification. [8](#0-7) 

---

### Recommendation

1. **Verify the signature in `handle_vote`**: After confirming committee membership, look up the staker's `public_key` from `self.committee.members()` and call `verify_precommit_vote_signature` (or an equivalent for prevotes). Reject the vote if verification fails.

2. **Reject zero public keys in `validate_stakers`**: Add a check analogous to the zero-weight filter:
   ```rust
   if staker.public_key == Felt::ZERO {
       return Err(CommitteeProviderError::ZeroPublicKey { address: staker.address });
   }
   ```
   This closes the secondary gap where a staker with `public_key: Felt::ZERO` would pass all existing guards and then cause `ecdsa_verify` to return `InvalidPublicKey` at runtime rather than being rejected at committee-construction time.

---

### Proof of Concept

```
1. Attacker connects to the sequencer's P2P network as a regular peer.

2. Attacker reads the current committee for height H (public on-chain data):
   committee = [VALIDATOR_A (addr=0x1), VALIDATOR_B (addr=0x2), VALIDATOR_C (addr=0x3)]
   quorum threshold = 2/3 of total weight

3. Attacker constructs forged precommit votes:
   forged_vote_A = Vote {
       vote_type: Precommit,
       height: H,
       round: 0,
       proposal_commitment: Some(attacker_chosen_commitment),
       voter: 0x1,                    // VALIDATOR_A's address
       signature: RawSignature::default(),  // all-zero, never checked
   }
   // repeat for VALIDATOR_B, VALIDATOR_C

4. Attacker broadcasts forged_vote_A, forged_vote_B, forged_vote_C via the
   consensus broadcast channel.

5. handle_vote() in SingleHeightConsensus:
   - height check: passes (H == H)
   - committee check: passes (0x1 is in committee)
   - signature check: SKIPPED (TODO comment)
   - vote accepted → state_machine.handle_event(Precommit(forged_vote_A))

6. After receiving forged votes for VALIDATOR_A, VALIDATOR_B, VALIDATOR_C,
   upon_decision() fires:
   - value_has_enough_votes: true (quorum reached with forged votes)
   - DecisionReached { block: attacker_chosen_commitment, round: 0 }

7. Node commits attacker_chosen_commitment as the decided block for height H.
``` [2](#0-1) [9](#0-8)

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

**File:** crates/apollo_staking_config/src/config.rs (L18-24)
```rust
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ConfiguredStaker {
    pub address: ContractAddress,
    pub weight: StakingWeight,
    pub public_key: Felt,
    pub can_propose: bool,
}
```

**File:** crates/apollo_staking/src/staking_manager.rs (L487-508)
```rust
fn validate_stakers(stakers: StakerSet) -> CommitteeProviderResult<StakerSet> {
    let mut seen_addresses = HashSet::with_capacity(stakers.len());
    for staker in &stakers {
        let new_address = seen_addresses.insert(staker.address);
        if !new_address {
            return Err(CommitteeProviderError::DuplicateStakerAddress { address: staker.address });
        }
    }

    let (valid_stakers, filtered): (StakerSet, StakerSet) =
        stakers.into_iter().partition(|staker| staker.weight.0 > 0);

    for staker in &filtered {
        warn!("Filtered out zero-weight staker {:?} from the staking response.", staker.address);
    }

    if valid_stakers.is_empty() {
        return Err(CommitteeProviderError::EmptyStakerSet);
    }

    Ok(valid_stakers)
}
```

**File:** crates/apollo_staking/src/staking_manager_test.rs (L35-39)
```rust
const STAKER_0: Staker = Staker {
    address: ContractAddress(PatriciaKey::from_hex_unchecked("0x0")),
    weight: StakingWeight(1000),
    public_key: Felt::ZERO,
};
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

**File:** crates/apollo_consensus/src/manager.rs (L993-1006)
```rust
            std::cmp::Ordering::Equal => match shc {
                Some(shc) => {
                    if self.cache.should_cache_vote(&height, shc.current_round(), &message) {
                        Ok(shc.handle_vote(message))
                    } else {
                        Ok(VecDeque::new())
                    }
                }
                None => {
                    trace!("Drop message from just completed height. {:?}", message);
                    Ok(VecDeque::new())
                }
            },
        }
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
