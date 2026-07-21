### Title
Precommit Vote Signature Omits `height`, `round`, `voter`, and `chain_id` — Voter Impersonation and Cross-Round Replay When Verification Is Wired In - (File: crates/apollo_signature_manager/src/signature_manager.rs)

### Summary

`build_precommit_vote_message_digest` signs only the `block_hash` field of a `Vote`. The `Vote` struct carries five additional fields — `vote_type`, `height`, `round`, `voter`, and (implicitly) `chain_id` — none of which are bound to the signature. When the consensus manager eventually wires in signature verification (the call site already exists and the TODO is explicit), any network peer who observes one valid precommit signature can replay it with a different `voter`, `round`, or on a different chain, forging quorum-weight votes from arbitrary validators.

### Finding Description

`build_precommit_vote_message_digest` constructs the signed payload as:

```
PRECOMMIT_VOTE || block_hash_bytes
``` [1](#0-0) 

The `Vote` struct that will carry this signature contains five additional fields that are **not** included in the digest: [2](#0-1) 

The consensus state machine creates self-votes with `RawSignature::default()` and an explicit TODO to sign them: [3](#0-2) 

`SingleHeightConsensus::handle_vote` accepts incoming votes with an explicit TODO to verify the signature: [4](#0-3) 

The `sign_precommit_vote` / `verify_precommit_vote_signature` pair is already wired into the `SignatureManager` component and its RPC handler, ready to be called: [5](#0-4) [6](#0-5) 

Because `voter` is absent from the digest, a valid `(r, s)` pair produced by validator A for `block_hash = X` is also a valid signature for a `Vote{voter: B, block_hash: X, height: H, round: R}`. Because `height` and `round` are absent, the same signature is valid for any `(height, round)` pair that references the same block hash. Because `chain_id` is absent, a signature produced on one network is valid on every other network that ever commits the same block hash.

### Impact Explanation

Once the two TODOs are resolved and signature verification is enforced:

1. **Voter impersonation / quorum forgery**: An attacker who observes a single valid precommit from validator A can resubmit it with `voter` set to any other committee member B. The signature still verifies because `voter` is not in the digest. By cycling through all committee members, the attacker can manufacture a 2/3+ quorum of precommits for any block hash that any one validator has legitimately signed, causing the consensus engine to reach a decision on a block that did not actually receive honest quorum support.

2. **Cross-round replay**: A precommit for `(height H, round R, block X)` is also a valid signature for `(height H, round R+k, block X)`. An attacker can replay old precommits in later rounds to steer the consensus outcome.

3. **Cross-chain replay**: No `chain_id` binding means a signature from a testnet validator is valid on mainnet for the same block hash.

The corrupted value is the `Decision` produced by `upon_decision`: it will record a block as having received honest 2/3+ precommit quorum when it did not. [7](#0-6) 

### Likelihood Explanation

The exploit requires no privileged access. Any p2p peer can observe broadcast votes (the vote channel is public gossip) and resubmit them with a modified `voter` field. The attack becomes active the moment the two TODO items are resolved — a natural next development step given that the `SignatureManager` component, its client trait, and the `verify_precommit_vote_signature` library function are all already present in production code.

### Recommendation

Include all vote fields in the signed digest:

```rust
fn build_precommit_vote_message_digest(vote: &Vote, chain_id: &ChainId) -> MessageDigest {
    let mut message = Vec::new();
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&chain_id.to_bytes());
    message.extend_from_slice(&vote.height.0.to_be_bytes());
    message.extend_from_slice(&vote.round.to_be_bytes());
    // vote_type is already domain-separated by PRECOMMIT_VOTE, but include it explicitly
    message.push(vote.vote_type as u8);
    message.extend_from_slice(vote.voter.0.key().to_bytes_be().as_ref());
    if let Some(pc) = &vote.proposal_commitment {
        message.extend_from_slice(&pc.0.to_bytes_be());
    }
    MessageDigest(blake2s_to_felt(&message))
}
```

This mirrors the Tendermint/CometBFT convention of signing the full canonical vote encoding and is consistent with the existing `build_peer_identity_message_digest` pattern that already binds both `peer_id` and `challenge`. [8](#0-7) 

### Proof of Concept

```
1. Honest validator A broadcasts Vote {
       vote_type: Precommit,
       height: 100,
       round: 0,
       proposal_commitment: Some(X),
       voter: A,
       signature: sig_A   // sign(PRECOMMIT_VOTE || X)
   }

2. Attacker observes the message on the p2p gossip channel.

3. Attacker rebroadcasts Vote {
       vote_type: Precommit,
       height: 100,
       round: 0,
       proposal_commitment: Some(X),
       voter: B,           // ← changed to any other committee member
       signature: sig_A    // ← unchanged; still valid because voter ∉ digest
   }

4. verify_precommit_vote_signature(X, sig_A, pubkey_A) == true
   (voter field is never checked against the signing key)

5. SingleHeightConsensus::handle_vote accepts the vote as coming from B,
   adding B's weight to the precommit tally for X.

6. By repeating for every committee member, attacker manufactures a
   2/3+ quorum from a single honest signature, triggering upon_decision.
``` [9](#0-8) [10](#0-9)

### Citations

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L68-74)
```rust
    pub async fn sign_precommit_vote(
        &self,
        block_hash: BlockHash,
    ) -> SignatureManagerResult<RawSignature> {
        let message_digest = build_precommit_vote_message_digest(block_hash);
        self.sign(message_digest).await
    }
```

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L127-136)
```rust
fn build_peer_identity_message_digest(peer_id: PeerId, challenge: Challenge) -> MessageDigest {
    let challenge = &challenge.0;
    let peer_id = peer_id.to_bytes();
    let mut message = Vec::with_capacity(INIT_PEER_ID.len() + peer_id.len() + challenge.len());
    message.extend_from_slice(INIT_PEER_ID);
    message.extend_from_slice(&peer_id);
    message.extend_from_slice(challenge);

    MessageDigest(blake2s_to_felt(&message))
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

**File:** crates/apollo_consensus/src/state_machine.rs (L248-256)
```rust
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

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L241-243)
```rust
    pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
        // TODO(Asmaa): verify the signature
        trace!("Received {:?}", vote);
```

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L249-252)
```rust
        if !self.committee.members().iter().any(|s| s.address == vote.voter) {
            debug!("Ignoring vote from non validator: vote={:?}", vote);
            return VecDeque::new();
        }
```

**File:** crates/apollo_signature_manager/src/communication.rs (L30-34)
```rust
            SignatureManagerRequest::SignPrecommitVote(block_hash) => {
                SignatureManagerResponse::SignPrecommitVote(
                    self.sign_precommit_vote(block_hash).await,
                )
            }
```
