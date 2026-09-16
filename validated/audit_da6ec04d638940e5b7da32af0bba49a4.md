### Title
Unbounded BEEFY Signature Count Enables Free CPU-Exhaustion via Unsigned `handle_unsigned` Extrinsics - (File: modules/consensus/beefy/verifier/src/lib.rs)

### Summary
`pallet-ismp`'s `handle_unsigned` call is an **unsigned, fee-less** extrinsic that every full node must fully execute (including consensus proof verification) just to admit it to the transaction pool. The BEEFY consensus verifier only enforces a *lower* bound on the number of signatures in a submitted proof (a supermajority threshold) but never an *upper* bound, so an attacker can submit a BEEFY consensus proof padded with an arbitrarily large number of bogus signatures. Each signature forces an expensive `secp256k1_recover` before the (ultimately failing) merkle membership check runs, so the attacker gets CPU amplification for free, replayable against every node on the network that validates the unsigned transaction.

### Finding Description
`check_participation_threshold` in `modules/consensus/beefy/verifier/src/lib.rs` only checks `len >= ((2 * total) / 3) + 1`: [1](#0-0) 

Immediately after that check, `verify_mmr_update_proof` iterates over `mmr.signed_commitment.signatures` — whose length is attacker-controlled — performing an ECDSA recovery (`H::secp256k1_recover`) for every entry, **before** the merkle multi-proof membership check (which would reject bogus authority indices) is evaluated: [2](#0-1) 

There is no cap tying `signatures_length` to `authority_set.len` (the real, small validator-set size), so an attacker can submit thousands of junk signatures far beyond the actual authority set size and still reach the recovery loop.

This verifier is reached from `pallet_ismp::Pallet::handle_unsigned`, which is declared `Unsigned` origin and is documented as executing "for free": [3](#0-2) 

Crucially, the `ValidateUnsigned::validate_unsigned` implementation **fully executes** the message batch (`Self::execute(messages.clone())`) merely to decide whether to admit the transaction to the pool: [4](#0-3) 

That execution path runs `update_client` → `consensus_client.verify_consensus` → `BeefyConsensusClient::verify_consensus` → `beefy_verifier::verify_consensus` → `verify_mmr_update_proof`: [5](#0-4) [6](#0-5) 

Because validation (not just execution after inclusion) runs this expensive recovery loop, **every node that receives the gossiped unsigned transaction** — not just the block author — pays the CPU cost of validating it, and the transaction ultimately fails (`InvalidAuthoritiesProof`/`BadProof`), costing the attacker nothing. This is the direct analog of CVE-2018-12545: cheap-to-submit, disproportionately expensive-to-process input (many "settings"/signatures) causing CPU-bound denial of service across the fleet of validating nodes, before any economically-costed rejection occurs.

The documentation explicitly claims the pool's validation "ensures... malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion" — but that filtering happens only *after* the expensive per-signature recovery loop runs, so the claimed mitigation does not actually bound CPU cost: [7](#0-6) 

Note: `EcdsaBeefy.sol` on the EVM side has an analogous unbounded loop (`for (uint256 i = 0; i < sigLen; i++) { ECDSA.recover(...) }` before the merkle-multi-proof check), but there the caller pays gas for every iteration and is bounded by the block gas limit, so it is a self-inflicted cost rather than a free-amplification DoS: [8](#0-7) 

### Impact Explanation
An attacker can craft a `handle_unsigned` extrinsic carrying a `Message::Consensus` payload whose BEEFY proof contains a large `signatures` vector (many thousands of garbage 65-byte entries, up to the node's max extrinsic/block-length limits), for a validator set they control the `validator_set_id` of (matching either `current_authorities.id` or `next_authorities.id`, which are public). The extrinsic is unsigned and free, and gets propagated/validated by every peer, forcing repeated expensive secp256k1 recoveries across the network. Because this validation happens for a class of transactions specifically carved out to be gas-free (to "not be exploited as a spam vector"), this directly undermines that stated protection, degrading node availability/liveness (CWE-400) network-wide — matching the High severity rating of the underlying Jetty CVE.

### Likelihood Explanation
High. No signature, no fee, and no special privilege is required — only knowledge of a currently valid `consensus_state_id` and the corresponding `validator_set_id`, both of which are public on-chain values. Any unprivileged relayer/user can build such a proof and gossip it repeatedly.

### Recommendation
Enforce an upper bound on the number of signatures/votes accepted in a BEEFY proof, tied to the real authority set size (e.g., reject if `signatures_length > authority_set.len`), and perform this bound check before entering the ECDSA-recovery loop, both in `beefy_verifier::verify_mmr_update_proof` (Rust) and in `EcdsaBeefy.verifyMmrUpdateProof` (Solidity). Consider also capping loop iterations/CPU work performed during `validate_unsigned` more generally (e.g., cheap sanity/size checks before full `execute`).

### Proof of Concept
1. Query the current `ConsensusState` for the BEEFY consensus client (public storage) to obtain `current_authorities.id`/`next_authorities.id` and the real authority set size `N` (e.g., a few hundred validators).
2. Construct a `ConsensusMessage` whose `commitment.validator_set_id` matches one of the above IDs.
3. Populate `signed_commitment.signatures` with `M >> N` (e.g., 50,000) syntactically-valid-but-bogus 65-byte ECDSA signatures (any values that pass basic decode), satisfying `check_participation_threshold` trivially since it only enforces a lower bound.
4. Submit `pallet_ismp::Call::handle_unsigned { messages: vec![Message::Consensus(msg)] }` as an unsigned extrinsic.
5. Observe that `validate_unsigned` on every receiving node executes `verify_mmr_update_proof`, performing `M` `secp256k1_recover` calls before failing the merkle multi-proof check — consuming significant CPU per node for a transaction the submitter paid nothing for. Repeating this with distinct payloads (to avoid dedupe via `provides` tag) sustains the amplification.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L145-175)
```rust
	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}

	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(mmr.authority_proof.clone());

	let valid = merkle_proof.verify(
		authority_set.keyset_commitment.into(),
		&authority_indices,
		&authority_leaves,
		authority_set.len as usize,
	);

	if !valid {
		Err(Error::InvalidAuthoritiesProof)?;
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-260)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

```

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-47)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
```

**File:** modules/ismp/clients/beefy/src/consensus.rs (L89-94)
```rust
		let (new_state, verified_parachains) = match *proof_type {
			PROOF_TYPE_NAIVE => {
				let consensus_proof: ConsensusMessage = codec::Decode::decode(&mut &payload[..])
					.map_err(|e| BeefyError::DecodeNaiveProof(format!("{e:?}")))?;
				verify_consensus::<SubstrateCrypto>(consensus_state, consensus_proof)?
			},
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L140-159)
```text
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();

        // verify the commitment
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }
```
