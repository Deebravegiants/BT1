## Title
Pre-authentication resource exhaustion via unbounded, fee-free `handle_unsigned` message batches re-validated on every node - (`modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp` exposes `handle_unsigned` as an unsigned, origin-less extrinsic (`ensure_none(origin)`), letting anyone submit ISMP message batches for free without a signature or fee. [1](#0-0)  Because it is unsigned, the runtime's `ValidateUnsigned::validate_unsigned` implementation is invoked by every full node's transaction pool logic on receipt/(re)validation of the gossiped extrinsic, and this implementation eagerly runs the *entire* message-execution pipeline — `Self::execute(messages.clone())` — including full cryptographic consensus verification, before the transaction is ever included in a block. [2](#0-1)  There is no cap on the size or number of `Message`s an attacker may submit in the `messages: Vec<Message>` argument, unlike the sibling `call-decompressor` pallet, which explicitly enforces `encoded_call_size < T::MaxCallSize::get() * ONE_MB` before doing any decompression work. [3](#0-2) 

This mirrors the ActiveMQ bug class described in the report: an unauthenticated peer can repeatedly submit "pre-session" protocol messages (there, `BrokerInfo` before `ConnectionInfo`; here, unsigned/unfunded `handle_unsigned` batches) that are processed and consume resources on every reachable node before any authentication, payment, or inclusion gate is satisfied, eventually exhausting CPU/memory across the network.

### Finding Description
`pallet_ismp::Pallet::handle_unsigned` only checks `ensure_none(origin)` — no signature check, no fee, no stake requirement — and then calls `Self::execute(messages.clone())`. [1](#0-0)  `execute` maps every message in the batch through `handle_incoming_message`, which for `Message::Consensus` dispatches to the configured consensus client's `verify_consensus`. [4](#0-3)  Depending on the configured client, this can mean full BEEFY MMR/authority-set merkle-multiproof verification with ECDSA signature recovery per signature, [5](#0-4)  or GRANDPA finality-proof verification with ancestry-chain construction. [6](#0-5) 

Critically, `ValidateUnsigned::validate_unsigned` for `pallet_ismp::Call::handle_unsigned` does not merely check well-formedness — it actually calls `Self::execute(messages.clone())` to compute the transaction's validity/priority tags. [2](#0-1)  Since `validate_unsigned` is the exact function substrate transaction pools invoke on every node that receives a gossiped unsigned extrinsic — and again on every pool revalidation pass — an attacker who varies message contents (so the resulting `provides` tag hash is unique, defeating the pool's dedup logic built for legitimate resubmissions) can force every reachable full node to repeatedly perform this expensive verification work, with no signature, no stake, and no fee ever charged, and no upper bound on the number/size of `Message`s in a single call.

This is functionally the same bug class as CVE-2026-50750: a message type that is processed by the receiving party before any authentication/session/payment gate is satisfied, and can be resent indefinitely by an unauthenticated party to exhaust the receiver's resources.

### Impact Explanation
An unauthenticated party (no relayer registration, no funds, no signed transaction) can force CPU/memory exhaustion across all full nodes running `pallet-ismp` by flooding the network with distinct, unbounded `handle_unsigned` batches containing costly `Message::Consensus`/`Message::Request` payloads (e.g., large authority sets, large merkle multiproofs, or many parachain headers). Because the check happens in `validate_unsigned` — which fires on every node before block inclusion and priority — this is a pre-authentication DoS vector reachable by any peer on the p2p gossip layer, matching the "unauthorized route unable to deliver messages" / DoS impact bar this scan accepts (High severity class, analogous to the ActiveMQ OOM report).

### Likelihood Explanation
High. `handle_unsigned` is deliberately public and unsigned by design (to let relayers submit for free), so no privileged capability, stake, or prior interaction is required. The only friction is constructing distinct-enough message batches to avoid the transaction pool's content-based dedup (`provides` tag), which is straightforward since the tag is a simple hash over attacker-controlled proof bytes. [7](#0-6) 

### Recommendation
Add a cheap, bounded pre-check (message count cap, max encoded size cap analogous to `call-decompressor`'s `MaxCallSize`, and/or a lightweight structural/format check) that is performed in `validate_unsigned` *before* calling `Self::execute`, so that malformed or oversized/abusive batches are rejected without running full consensus verification. Consider deferring full `execute()` execution to `pre_dispatch`/block application only, and having `validate_unsigned` perform a cheaper sufficiency check (e.g., signature/proof shape validation and a per-source rate limit) instead of full cryptographic verification on every gossip/revalidation pass.

### Proof of Concept
1. Construct many distinct unsigned extrinsics calling `pallet_ismp::Call::handle_unsigned { messages }`, each carrying a `Message::Consensus` with a large but syntactically valid-looking `consensus_proof` (e.g., maximal authority-set merkle multiproof / many BEEFY signatures) so each triggers `verify_mmr_update_proof`'s per-signature ECDSA recovery loop. [8](#0-7) 
2. Vary `consensus_proof` bytes slightly per submission so each produces a unique `provides` tag hash, bypassing the pool's dedup logic. [9](#0-8) 
3. Submit these unsigned extrinsics repeatedly to the p2p network as an unauthenticated peer with no funds.
4. Each receiving full node's transaction pool calls `validate_unsigned`, which runs `Self::execute` and thus the full expensive verification path, for every submission and on every revalidation cycle — with no cap on batch size/count, driving up CPU and memory usage network-wide without the attacker ever paying a fee or requiring a signed identity.

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

**File:** modules/pallets/ismp/src/lib.rs (L614-625)
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

**File:** modules/pallets/ismp/src/lib.rs (L658-699)
```rust
			let mut has_consensus = false;
			let mut tags = messages
				.into_iter()
				.map(|message| match message {
					Message::Consensus(ConsensusMessage {
						consensus_proof,
						consensus_state_id,
						..
					}) => {
						has_consensus = true;
						vec![H256(sp_io::hashing::keccak_256(
							&(consensus_state_id, consensus_proof).encode(),
						))]
					},
					Message::FraudProof(FraudProofMessage { proof_1, proof_2, .. }) => vec![
						H256(sp_io::hashing::keccak_256(&proof_1)),
						H256(sp_io::hashing::keccak_256(&proof_2)),
					],
					Message::Request(RequestMessage { requests, .. }) => requests
						.into_iter()
						.map(|post| hash_request::<Pallet<T>>(&Request::Post(post.clone())))
						.collect::<Vec<_>>(),
					Message::Response(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
					Message::Timeout(message) => message
						.requests()
						.iter()
						.map(|request| hash_request::<Pallet<T>>(request))
						.collect::<Vec<_>>(),
				})
				.collect::<Vec<_>>();
			tags.sort();

			if tags.is_empty() {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&tags.encode()).to_vec();
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L113-118)
```rust
		) -> DispatchResult {
			ensure_none(origin)?;
			ensure!(
				encoded_call_size < T::MaxCallSize::get() * ONE_MB,
				Error::<T>::CallSizeOutOfBound
			);
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

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L69-90)
```rust
	fn verify_consensus(
		&self,
		_host: &dyn IsmpHost,
		consensus_state_id: ConsensusStateId,
		trusted_consensus_state: Vec<u8>,
		proof: Vec<u8>,
	) -> Result<(Vec<u8>, VerifiedCommitments), Error> {
		// decode the proof into consensus message
		let consensus_message: ConsensusMessage = codec::Decode::decode(&mut &proof[..])
			.map_err(|e| GrandpaError::DecodeConsensusMessage(format!("{e:?}")))?;

		// decode the consensus state
		let consensus_state: ConsensusState =
			codec::Decode::decode(&mut &trusted_consensus_state[..])
				.map_err(|e| GrandpaError::DecodeConsensusState(format!("{e:?}")))?;

		// Reject before any arm runs; see `envelope_matches_state_machine`.
		if !envelope_matches_state_machine(&consensus_state.state_machine, &consensus_message) {
			Err(GrandpaError::ConsensusMessageStateMachineMismatch(
				consensus_state.state_machine,
			))?
		}
```
