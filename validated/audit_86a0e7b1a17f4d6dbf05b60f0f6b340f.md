### Title
Precommit Vote Signature Message Digest Omits `chain_id`, Enabling Cross-Chain Replay of Consensus Votes — (`crates/apollo_signature_manager/src/signature_manager.rs`)

### Summary

`build_precommit_vote_message_digest` constructs the signed payload as `blake2s("PRECOMMIT_VOTE" || block_hash)` with no `chain_id` field. When precommit vote signing is wired into the consensus state machine (currently a `TODO`), a validator's ECDSA precommit signature produced on one Starknet chain is cryptographically identical to a valid signature for the same block hash on any other chain, enabling cross-chain replay of consensus votes.

### Finding Description

`build_precommit_vote_message_digest` at line 138–145 of `crates/apollo_signature_manager/src/signature_manager.rs` computes:

```
blake2s( b"PRECOMMIT_VOTE" || block_hash.to_bytes_be() )
``` [1](#0-0) 

No `chain_id` is mixed into the digest. The symmetric verification path `verify_precommit_vote_signature` uses the same construction: [2](#0-1) 

The `sign_precommit_vote` entry point is already exposed through the `SignatureManagerClient` trait and `SignatureManagerRequest::SignPrecommitVote(BlockHash)`: [3](#0-2) 

The consensus state machine currently defers signing with explicit `TODO` markers: [4](#0-3) [5](#0-4) 

The `block_hash` value itself is computed by `calculate_block_hash`, which does **not** include `chain_id` directly — chain-specificity comes only from the `previous_block_hash` chain back to genesis: [6](#0-5) 

The `PartialBlockHash` used in `ProposalCommitment` is even weaker: it substitutes fixed zero constants for both `state_root` and `parent_hash`, completely severing the genesis chain: [7](#0-6) 

This means a `PartialBlockHash` carries **no chain-specific entropy at all**, and if `sign_precommit_vote` is ever called with a value derived from `PartialBlockHash`, the replay surface is maximally broad.

### Impact Explanation

When precommit signing is enabled, an attacker who observes a quorum of precommit signatures for block hash `H` on chain A (e.g., mainnet) can submit those same signatures verbatim on chain B (e.g., a testnet or fork that shares the same genesis or the same `PartialBlockHash` value). Because the digest is `blake2s("PRECOMMIT_VOTE" || H)` on both chains, every signature verifies correctly. This allows forging a 2/3 quorum on chain B without any validator on chain B having actually voted, causing an unauthorized block to be finalized. The impact matches: **"High. Transaction conversion or signature/hash logic binds the wrong signer, hash, type, or executable payload."**

### Likelihood Explanation

The vulnerability is latent today because vote signing is a `TODO`. However, the production function is already written incorrectly, and the `SignatureManagerClient` interface is already wired. The moment signing is activated, any two Starknet networks sharing a genesis block hash (e.g., integration testnet, a fork, or a chain that reuses the same sequencer address and gas prices) become vulnerable. The `PartialBlockHash` path (zero parent hash) makes the collision surface even larger.

### Recommendation

Include `chain_id` in the message digest before the block hash:

```rust
fn build_precommit_vote_message_digest(
    block_hash: BlockHash,
    chain_id: &ChainId,
) -> MessageDigest {
    let block_hash = block_hash.to_bytes_be();
    let chain_id_bytes = Felt::try_from(chain_id)
        .expect("chain_id must be ASCII")
        .to_bytes_be();
    let mut message = Vec::with_capacity(
        PRECOMMIT_VOTE.len() + chain_id_bytes.len() + block_hash.len(),
    );
    message.extend_from_slice(PRECOMMIT_VOTE);
    message.extend_from_slice(&chain_id_bytes);
    message.extend_from_slice(&block_hash);
    MessageDigest(blake2s_to_felt(&message))
}
```

Propagate `chain_id` through `sign_precommit_vote` and `verify_precommit_vote_signature` accordingly. The `SignatureManager` already holds a `chain_id` field in `TransactionConverter`; a similar field should be added to `SignatureManager`.

### Proof of Concept

1. Validator `V` signs a precommit on **chain A** (mainnet) for block hash `H`:
   `sig = ecdsa_sign(privkey_V, blake2s("PRECOMMIT_VOTE" || H))`

2. On **chain B** (testnet/fork), the same block hash `H` appears (same block number, same transactions, same gas prices, same sequencer — or simply the same `PartialBlockHash` because it uses zero parent hash).

3. An attacker submits `sig` as a precommit vote from `V` on chain B. `verify_precommit_vote_signature(H, sig, pubkey_V)` computes `blake2s("PRECOMMIT_VOTE" || H)` — identical to chain A — and returns `true`.

4. Repeating for enough validators to reach the 2/3 quorum threshold causes chain B to finalize a block that no validator on chain B ever legitimately voted for. [1](#0-0) [2](#0-1)

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

**File:** crates/apollo_signature_manager/src/signature_manager.rs (L179-185)
```rust
pub fn verify_precommit_vote_signature(
    block_hash: BlockHash,
    signature: RawSignature,
    public_key: PublicKey,
) -> SignatureVerificationResult<bool> {
    let message_digest = build_precommit_vote_message_digest(block_hash);
    verify_signature(message_digest, signature, public_key)
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

**File:** crates/apollo_consensus/src/single_height_consensus.rs (L241-243)
```rust
    pub(crate) fn handle_vote(&mut self, vote: Vote) -> Requests {
        // TODO(Asmaa): verify the signature
        trace!("Received {:?}", vote);
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L189-206)
```rust
impl PartialBlockHash {
    // TODO(Ariel): Use parent_partial_block_hash instead of zero.
    const GLOBAL_ROOT_FOR_PARTIAL_BLOCK_HASH: GlobalRoot = GlobalRoot(Felt::ZERO);
    const PARENT_HASH_FOR_PARTIAL_BLOCK_HASH: BlockHash = BlockHash(Felt::ZERO);

    /// Hash of [`PartialBlockHashComponents`].
    /// Uses the same formula as [`calculate_block_hash`] with the fixed constants above for the
    /// state root and parent hash.
    pub fn from_partial_block_hash_components(
        partial_block_hash_components: &PartialBlockHashComponents,
    ) -> StarknetApiResult<Self> {
        let block_hash = calculate_block_hash(
            partial_block_hash_components,
            Self::GLOBAL_ROOT_FOR_PARTIAL_BLOCK_HASH,
            Self::PARENT_HASH_FOR_PARTIAL_BLOCK_HASH,
        )?;
        Ok(Self(block_hash.0))
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
