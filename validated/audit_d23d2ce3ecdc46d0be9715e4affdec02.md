### Title
Precommit Vote Signature Missing Chain ID, Height, and Round — (`crates/apollo_signature_manager/src/signature_manager.rs`)

### Summary

`build_precommit_vote_message_digest` constructs the signed payload for a consensus precommit vote using only a static domain tag and the `block_hash`. It omits `chain_id`, `height`, and `round`. This is the direct Sequencer analog of the NFT `preMint()` bug: a signature produced for one context (chain, height, or round) is cryptographically valid in any other context that shares the same `block_hash`.

### Finding Description

`build_precommit_vote_message_digest` in `crates/apollo_signature_manager/src/signature_manager.rs` constructs the message digest as:

```rust
fn build_precommit_vote_message_digest(block_hash: BlockHash) -> MessageDigest {
    let block_hash = block_hash.to_bytes_be();
    let mut message = Vec::with_capacity(PRECOMMIT_VOTE.len() + block_hash.len());
    message.extend_from_slice(PRECOMMIT_VOTE);   // b"PRECOMMIT_VOTE"
    message.extend_from_slice(&block_hash);
    MessageDigest(blake2s_to_felt(&message))
}
``` [1](#0-0) 

The signed payload is `PRECOMMIT_VOTE || block_hash`. The `Vote` struct carries `height`, `round`, `voter`, and `proposal_commitment` alongside the `signature`, but none of those fields are bound into the digest. [2](#0-1) 

The public API `sign_precommit_vote` and `verify_precommit_vote_signature` both delegate to this function: [3](#0-2) [4](#0-3) 

The consensus state machine currently sets `signature: RawSignature::default()` with a `TODO(Asmaa): sign the vote` comment, and `handle_vote` has a matching `TODO(Asmaa): verify the signature` comment: [5](#0-4) [6](#0-5) 

The signing infrastructure is complete and exposed over the component RPC (`SignatureManagerRequest::SignPrecommitVote`); only the call-sites in the consensus loop are pending. The flaw is therefore baked into the scheme that will be activated. [7](#0-6) 

### Impact Explanation

Once vote signing and verification are wired in, a validator's precommit signature for `block_hash = H` at `(chain=A, height=N, round=R)` is byte-for-byte identical to a valid signature for `block_hash = H` at `(chain=B, height=M, round=S)`. Concretely:

1. **Cross-chain replay**: A precommit collected on a testnet/devnet instance can be injected into a mainnet consensus round that happens to produce the same `ProposalCommitment` value. Because `chain_id` is absent from the digest, `verify_precommit_vote_signature` returns `true` on both chains.
2. **Cross-height/round replay**: If the same block content (and therefore the same `block_hash`) is re-proposed at a different height or round (e.g., after a fork or re-org scenario), a precommit from the earlier round is valid for the later one. This can artificially satisfy the 2/3 quorum check in `upon_decision`, causing the state machine to commit a block that did not actually receive fresh quorum at the current height/round. [8](#0-7) 

### Likelihood Explanation

The trigger requires the same `block_hash` to appear in two different contexts. Block hashes are derived from transaction hashes that include `chain_id`, making accidental cross-chain collision unlikely but not impossible (empty blocks, deterministic test blocks). Cross-height replay within the same chain is more realistic: a proposer can re-propose an identical block at a new height or round, and any precommit signatures collected in the earlier round remain valid. The attack is unprivileged once the signing TODO is resolved — any network participant who observed a prior precommit can replay it.

### Recommendation

Bind all context-identifying fields into the digest:

```rust
fn build_precommit_vote_message_digest(
    chain_id: &ChainId,
    height: BlockNumber,
    round: Round,
    block_hash: BlockHash,
) -> MessageDigest {
    let mut message = Vec::new();
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&Felt::try_from(chain_id).unwrap().to_bytes_be());
    message.extend_from_slice(&height.0.to_be_bytes());
    message.extend_from_slice(&round.to_be_bytes());
    message.extend_from_slice(&block_hash.to_bytes_be());
    MessageDigest(blake2s_to_felt(&message))
}
```

`SignatureManager` should receive `chain_id` at construction time (mirroring `TransactionConverter`), and `sign_precommit_vote` / `verify_precommit_vote_signature` should accept `height` and `round` as parameters. The existing TODO note in the file already flags a related delimiter-ambiguity concern: [9](#0-8) 

### Proof of Concept

1. Validator V signs a precommit for `block_hash = X` at `(chain=mainnet, height=100, round=0)`. The raw signature bytes are `sig_X`.
2. The same block content is re-proposed at `(chain=mainnet, height=101, round=0)` (or on a shadow testnet), producing the same `block_hash = X`.
3. An attacker injects `Vote { height=101, round=0, voter=V, proposal_commitment=X, signature=sig_X }` into the p2p layer.
4. `verify_precommit_vote_signature(X, sig_X, V.public_key)` returns `true` because the digest is `blake2s("PRECOMMIT_VOTE" || X)` — identical in both contexts.
5. The replayed vote counts toward the 2/3 quorum at height 101, potentially allowing a block to be committed without V's genuine participation at that height. [1](#0-0) [8](#0-7)

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

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L122-124)
```rust
// TODO(noam.s): Consider wrapping each field in fixed delimiters (e.g. parentheses or tags) to
// avoid delimiter ambiguity across implementations; see apollo_propeller/signature.rs and PR
// review.
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

**File:** crates/apollo_signature_manager/src/communication.rs (L30-34)
```rust
            SignatureManagerRequest::SignPrecommitVote(block_hash) => {
                SignatureManagerResponse::SignPrecommitVote(
                    self.sign_precommit_vote(block_hash).await,
                )
            }
```
