### Title
Free, uncapped mempool-time execution of `handle_unsigned` lets an attacker force every full node to repeatedly run expensive consensus/proof verification at zero cost - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet-ismp` accepts cross-chain messages (including consensus updates) as **unsigned, fee-free extrinsics**. Transaction-pool admission for `handle_unsigned` is decided by fully executing the message batch — including the whole consensus-proof verification path (ECDSA/BLS signature checks, SP1 Groth16 proof verification, merkle multiproofs, MMR verification, etc.) — inside `validate_unsigned`, and this same expensive execution is repeated again at block-inclusion time and again on every pool re-validation for the transaction's `longevity` window.

### Finding Description
`Pallet::validate_unsigned` calls `Self::execute(messages.clone())` to decide if an unsigned `handle_unsigned` transaction should enter the mempool: [1](#0-0) 

`Self::execute` runs the full ISMP dispatch pipeline for every message in the batch, invoking `handle_incoming_message`, which for a `Message::Consensus` routes straight into `consensus::update_client`: [2](#0-1) [3](#0-2) 

`update_client` immediately calls the concrete `ConsensusClient::verify_consensus` implementation with the untrusted `msg.consensus_proof` — no cheap, unforgeable pre-check gates the expensive cryptography: [4](#0-3) 

The consensus clients only skip verification for trivially stale heights (a field the attacker fully controls and can set to any non-stale value), so the attacker can always force the full expensive path to run:
- BEEFY (ECDSA path): loops `ecrecover` over every submitted signature and a merkle multi-proof of the whole authority set before it can determine the proof is invalid: [5](#0-4) 
- BEEFY (SP1 path): runs a full Groth16 verification of an attacker-supplied proof blob: [6](#0-5) 
- Sync-committee (Ethereum): runs BLS aggregate-signature verification and multiple SSZ merkle-branch checks: [7](#0-6) 
- BSC/Tendermint clients likewise only bail out on a stale-height check before doing header/consensus verification work: [8](#0-7) 

None of this work costs the sender anything: `handle_unsigned` is documented and implemented to "execute for free", with `ensure_none(origin)` as the only origin check: [9](#0-8) [10](#0-9) 

Because a Substrate transaction pool re-validates queued extrinsics on every new best block (up to the declared `longevity`, here `25`) and every peer node independently re-runs `validate_unsigned` on propagation, a single crafted-but-invalid consensus message with a fresh (non-stale) height and a syntactically well-formed but cryptographically bogus proof forces **every node in the network** to repeatedly pay for full signature/proof verification, for free, for up to 25 blocks, and the attacker can trivially generate many such distinct messages (differing by height/nonce) to multiply the effect, since each yields a unique `provides` tag and is accepted into the pool independently.

This is the direct structural analog of CVE-2018-19162: a network participant who spends essentially nothing (no stake, no fee — here literally zero cost since it's unsigned and un-metered pre-verification) can force disproportionately expensive processing (there: disk-persisted invalid headers; here: CPU-bound cryptographic verification) on every honest node, which is a classic asymmetric-cost remote DoS.

### Impact Explanation
This is a network-wide availability attack against every collator/full node running `pallet-ismp` with the `unsigned` feature enabled (the standard configuration per the docs and tests). Sustained spam of syntactically-valid-but-cryptographically-invalid consensus messages can consume disproportionate CPU on all nodes during both mempool validation and block-import re-validation, potentially degrading block production/import throughput or making other unsigned/legitimate consensus updates race for pool space, without the attacker paying any transaction fee. It targets a permissionless entry point reachable by "an unprivileged message dispatcher, relayer, token bridger" as required by scope, since anyone can submit unsigned `handle_unsigned` extrinsics containing a `Message::Consensus`.

### Likelihood Explanation
Likelihood is high: constructing an invalid-but-non-stale consensus proof requires no privileged access, no stake, and no fee — only crafting the SCALE-encoded `ConsensusMessage` with a height beyond `latest_beefy_height`/`finalized_height` (a public, queryable value) and arbitrary bytes for the signature/proof fields. This can be automated and broadcast continuously from any P2P-connected node. The only mitigating factor observed is the runtime-level `IsmpCallFilter` in `gargantua`/`nexus` runtimes, which rejects raw BEEFY updates through `handle_unsigned` in favor of `pallet-beefy-consensus-proofs`, but that filter does not appear to exist for other consensus clients (BSC, Tendermint, sync-committee, Arbitrum, Optimism) reachable via `handle_unsigned`, so the exposure is client- and runtime-dependent and not verified to be closed everywhere.

### Recommendation
- Gate `validate_unsigned` for consensus messages behind a cheap, unforgeable admission cost before invoking full cryptographic verification — e.g., require a bond/fee for consensus-message submission even though delivery itself remains free on success, or rate-limit unsigned consensus submissions per source/per consensus_state_id in the transaction pool.
- Apply the same `IsmpCallFilter`-style routing used for BEEFY (forcing proofs through a fee/deposit-gated pallet like `pallet-beefy-consensus-proofs`) uniformly to all consensus clients reachable via `handle_unsigned`, not just BEEFY.
- Consider caching/memoizing "already proven invalid" proof hashes so repeated pool re-validation of the same payload does not redo the expensive verification for the whole `longevity` window.
- Add a much cheaper structural/format pre-check (e.g., signature count bounds, basic format sanity) ahead of `verify_consensus` so obviously malformed spam is rejected before expensive crypto runs, though note the attacker can still submit well-formed-but-fraudulent proofs, so this alone is not sufficient.

### Proof of Concept
1. Query the public consensus state for a target `consensus_state_id` (e.g. via `query_consensus_state`) to learn `latest_beefy_height` / `finalized_height`.
2. Construct a `ConsensusMessage` whose `consensus_proof` encodes a `RelayChainProof`/`ParachainProof` (or BSC/Tendermint/sync-committee equivalent) with `block_number = latest_height + 1` and syntactically valid but cryptographically bogus signatures/merkle proofs (e.g., random 65-byte ECDSA signatures for every authority slot to pass length checks and force `ecrecover` + merkle multiproof verification, and a `MiniCommitment`/SP1 proof blob with a plausible layout to force `Groth16Verifier::verify`).
3. Wrap it in `Call::handle_unsigned { messages: vec![Message::Consensus(msg)] }` and submit as an unsigned extrinsic via `create_unsigned`/RPC to a node.
4. Observe that `validate_unsigned` (modules/pallets/ismp/src/lib.rs:614) executes the full verification path (`beefy_verifier::verify_consensus` / `verify_sp1_consensus` / `verify_sync_committee_attestation` / BSC `verify_bsc_header`) before rejecting the transaction as `InvalidTransaction::BadProof`.
5. Repeat with distinct heights/nonces to generate many uniquely-tagged pool entries and measure aggregate CPU/verification time across a multi-node testnet versus the (zero) cost paid by the attacker; each node independently repeats this work on gossip propagation and on pool maintenance for up to 25 blocks.

### Citations

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

**File:** modules/pallets/ismp/src/impls.rs (L40-51)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;
```

**File:** modules/ismp/core/src/handlers.rs (L86-100)
```rust
pub fn handle_incoming_message<H>(
	host: &H,
	message: Message,
) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	match message {
		Message::Consensus(consensus_message) => consensus::update_client(host, consensus_message),
		Message::FraudProof(fraud_proof) => consensus::freeze_client(host, fraud_proof),
		Message::Request(req) => request::handle(host, req),
		Message::Response(resp) => response::handle(host, resp),
		Message::Timeout(timeout) => timeout::handle(host, timeout),
	}
}
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L33-46)
```rust
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
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-176)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

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

**File:** modules/consensus/beefy/verifier/src/sp1.rs (L93-109)
```rust
	let public_inputs = PublicInputs {
		authorities_root: FixedBytes::from(Into::<[u8; 32]>::into(authority.keyset_commitment)),
		authorities_len: U256::from(authority.len),
		leaf_hash: FixedBytes::from(Into::<[u8; 32]>::into(H::keccak256(&proof.mmr_leaf.encode()))),
		block_number: U256::from(proof.block_number),
		headers,
		nonce: FixedBytes::from(proof.nonce.0),
	}
	.abi_encode();

	sp1_verifier::Groth16Verifier::verify(
		&proof.proof,
		&public_inputs,
		vkey,
		sp1_verifier::GROTH16_VK_BYTES,
	)
	.map_err(|_| Error::Sp1VerificationFailed)?;
```

**File:** modules/consensus/sync-committee/verifier/src/lib.rs (L85-93)
```rust
	// Verify sync committee aggregate signature
	let sync_committee = if update_signature_period == state_period {
		trusted_state.current_sync_committee.clone()
	} else {
		trusted_state.next_sync_committee.clone()
	};

	let sync_committee_pubkeys = sync_committee.public_keys;
	let sync_committee_bits = update.sync_aggregate.sync_committee_bits;
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L88-93)
```rust
		if consensus_state.finalized_height >= bsc_client_update.source_header.number.low_u64() {
			Err(Error::ExpiredUpdate {
				current: consensus_state.finalized_height,
				update: bsc_client_update.source_header.number.low_u64(),
			})?
		}
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```
