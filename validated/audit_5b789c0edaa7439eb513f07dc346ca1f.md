## Title
Unbounded compute in `pallet-ismp`'s `handle_unsigned` mempool validation enables free-of-charge resource-exhaustion analogous to CVE-2022-1431 - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet_ismp::Pallet::<T>::handle_unsigned` is dispatched as an **unsigned** extrinsic, meaning every node's transaction pool calls `ValidateUnsigned::validate_unsigned`, which in turn calls `Self::execute(messages.clone())` — running the *full* ISMP message-handling pipeline (proof decoding, trie/MMR/multiproof verification, EVM storage-proof reconstruction, etc.) against attacker-supplied `Vec<Message>` before any fee is charged and before the transaction is even included in a block.

### Finding Description
The GitLab CVE (BIT-gitlab-2022-1431 / CVE-2022-1431) is about an unauthenticated API endpoint performing uncontrolled resource consumption because attacker-controlled request parameters are not size-bounded before expensive processing happens. The same *bug class* is reachable here:

- `handle_unsigned` accepts an arbitrary `Vec<Message>` with no visible bound on the number of messages, number of requests per message, or number of keys per `GetRequest`: [1](#0-0) 

- Because this is registered as an unsigned call, `ValidateUnsigned::validate_unsigned` executes the same expensive path — `Self::execute(messages.clone())` — on **every node** during mempool admission, *before* any fee/weight accounting takes effect and before block inclusion: [2](#0-1) 

- `execute()` maps every message through `handle_incoming_message`, which for `Message::Request`/`Message::Response` performs full membership/non-membership proof verification (`verify_membership`, `verify_state_proof`) over all keys/requests supplied in the batch: [3](#0-2) 

- Downstream, `verify_state_proof` implementations (Substrate EVM, Pharos, Substrate trie) decode and walk tries/child-tries per key with no visible cap on `keys.len()`: [4](#0-3) [5](#0-4) 

- Similarly, `pallet_state_coprocessor::handle_unsigned` runs `handle_get_requests`, which performs the same unbounded-by-request-count proof verification during `validate_unsigned`: [6](#0-5) [7](#0-6) 

I could not locate an explicit `MaxMessages`/`MaxKeys`/`BoundedVec` type constraining the size of `messages: Vec<Message>` or `GetRequest.keys: Vec<Vec<u8>>` inside `pallet-ismp` or `pallet-state-coprocessor` in the indexed code, nor a byte-size cap analogous to `call-decompressor`'s `MaxCallSize` gate that specifically protects `handle_unsigned`. The `call-decompressor` pallet does bound decompressed call size before decoding (`Error::<T>::CallSizeOutOfBound`) as a mitigation for a similar zstd-bomb class of bug, which shows the team is aware of this bug class in one code path but I could not confirm the same protection exists directly ahead of `handle_unsigned`'s own execution: [8](#0-7) 

### Impact Explanation
If the number of messages/requests/keys per `handle_unsigned` call is unbounded, a single relayed extrinsic (reachable by any unprivileged actor, since `handle_unsigned` is a free, permissionless unsigned call intended for relayers) can force every full node's mempool-validation logic to perform disproportionately expensive cryptographic/trie work relative to the extrinsic's size on the wire. Because this validation runs before block inclusion and before weight-based fee metering applies (the call is free/unsigned), repeated submission of such payloads is a network-wide DoS vector against the parachain's transaction pool and could degrade or halt relayer message delivery (a "route unable to deliver messages" condition) network-wide.

### Likelihood Explanation
Likelihood depends entirely on whether an actual size cap exists elsewhere in the runtime configuration (e.g., `frame_system::Config::BlockLength` / extrinsic size limits, or a bound I did not find in the indexed portions of the codebase) that effectively caps `messages.len()` and `keys.len()` by capping the whole extrinsic's encoded byte size. Standard Substrate runtimes do cap block/extrinsic length, which would bound the *total bytes* of the attack payload, though it would not necessarily prevent an attacker from packing many small, individually-cheap-looking keys/requests that in aggregate cause expensive trie decoding relative to their encoded size (e.g., many repeated/near-duplicate storage proof entries). I was not able to fully verify the presence or absence of extrinsic-length limits or dedicated `MaxMessages`/`MaxKeys` bounds for this specific call path within the scope of my search, so I cannot confirm this is exploitable as stated with full confidence.

### Recommendation
- Add explicit, enforced bounds (e.g., `BoundedVec` with a `MaxMessages`/`MaxRequestsPerMessage`/`MaxKeysPerRequest` config constant) on `messages: Vec<Message>` passed to `pallet_ismp::handle_unsigned` and on `GetRequestsWithProof.requests`/`GetRequest.keys` passed to `pallet_state_coprocessor::handle_unsigned`, enforced in `validate_unsigned` *before* any proof decoding/verification begins.
- Ensure `validate_unsigned` performs cheap, size/shape checks (batch/key/proof-node counts) prior to any trie or cryptographic verification, mirroring the `MAX_PROOF_DEPTH` guard already present in the Pharos SPV code: [9](#0-8) 

### Proof of Concept
Not constructed — I could not confirm within the indexed codebase whether an effective upper bound on `messages.len()`/`keys.len()` already exists elsewhere in the runtime (e.g., transaction/block length limits), which is necessary to determine whether this is concretely exploitable versus already mitigated. Given this unresolved uncertainty, and per the requirement to prove root cause with exact file/function support at a Medium-or-higher confidence, I present this as a candidate finding with an explicit caveat rather than a fully substantiated vulnerability.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
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

**File:** modules/ismp/state-machines/evm/src/substrate_evm.rs (L182-248)
```rust
	fn verify_state_proof(
		&self,
		_host: &dyn IsmpHost,
		keys: Vec<Vec<u8>>,
		root: H256,
		proof: &Proof,
	) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
		let ismp_host_address = EvmHosts::<T>::get(&proof.height.id.state_id)
			.ok_or(SubstrateEvmError::IsmpContractNotFound)?;

		let proof: SubstrateEvmProof =
			Decode::decode(&mut &proof.proof[..]).map_err(SubstrateEvmError::ProofDecodeError)?;

		let state_root = root;

		let keys_len = keys.len();
		let mut contract_keys: BTreeMap<H160, Vec<Vec<u8>>> = BTreeMap::new();
		for key in keys {
			let address = if key.len() == 52 {
				H160::from_slice(&key[..20])
			} else if key.len() == 32 {
				ismp_host_address
			} else {
				return Err(SubstrateEvmError::InvalidKeyLength(key.len()).into());
			};
			contract_keys.entry(address).or_default().push(key);
		}

		let mut result_map = BTreeMap::new();

		for (address, keys) in contract_keys {
			let contract_info_key = contract_info_key(address);
			let trie_id = fetch_trie_id_from_main_proof::<H>(
				&proof.main_proof,
				state_root,
				&contract_info_key,
			)?;

			let child_root =
				fetch_child_root_from_main_proof::<H>(&proof.main_proof, state_root, &trie_id)?;

			let storage_proof = proof
				.storage_proof
				.get(address.as_bytes())
				.ok_or(SubstrateEvmError::StorageProofMissing(address.as_bytes().to_vec()))?;

			let storage_keys: Vec<Vec<u8>> = keys
				.iter()
				.map(|k| {
					let slot = if k.len() == 52 { &k[20..] } else { &k[..] };
					blake2_256(slot).to_vec()
				})
				.collect();

			let values = verify_child_trie_values::<H>(child_root, storage_proof, storage_keys)?;

			for (key, value) in keys.into_iter().zip(values.into_iter()) {
				result_map.insert(key, value);
			}
		}

		if result_map.len() != keys_len {
			return Err(SubstrateEvmError::MismatchedValuesAndKeys.into());
		}

		Ok(result_map)
	}
```

**File:** modules/ismp/state-machines/pharos/src/lib.rs (L238-336)
```rust
/// Verify state proof and return key-value map.
pub fn verify_state_proof<H: Keccak256 + Send + Sync>(
	keys: Vec<Vec<u8>>,
	root: H256,
	proof: &Proof,
	ismp_address: H160,
) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
	let pharos_proof = decode_pharos_state_proof(proof)?;

	let state_root = root;

	// Pharos uses a flat trie — storage proofs verify directly against state_root.
	let mut map = BTreeMap::new();

	for key in keys {
		let (contract_addr, slot_hash) = if key.len() == 52 {
			// First 20 bytes = contract address, last 32 = slot hash
			let addr = H160::from_slice(&key[..20]);
			(addr, key[20..].to_vec())
		} else if key.len() == 32 {
			// Direct slot hash for the ISMP host contract
			(ismp_address, key.clone())
		} else if key.len() == 20 {
			// Account query which verifies account proof and return raw account value
			let address: [u8; 20] = key
				.clone()
				.try_into()
				.map_err(|e: Vec<u8>| PharosStateMachineError::InvalidAddressLength(e.len()))?;
			let account_data = pharos_proof
				.account_proofs
				.get(&key)
				.ok_or(PharosStateMachineError::MissingAccountProof)?;

			spv::verify_proof(
				&account_data.proof_nodes,
				&address,
				&account_data.raw_value,
				&state_root.0,
			)
			.map_err(|e| PharosStateMachineError::SpvVerificationFailed(alloc::format!("{e:?}")))?;

			map.insert(key, Some(account_data.raw_value.clone()));
			continue;
		} else {
			return Err(PharosStateMachineError::UnsupportedKeyLength.into());
		};

		let contract_address: [u8; 20] = contract_addr.0;

		let slot_key: [u8; 32] = slot_hash
			.clone()
			.try_into()
			.map_err(|e: Vec<u8>| PharosStateMachineError::InvalidSlotHashLength(e.len()))?;

		// Check if this is a non-existence proof
		if let Some(non_existence) = pharos_proof.non_existence_proofs.get(slot_key.as_slice()) {
			spv::verify_non_existence_proof(
				&non_existence.proof_nodes,
				&spv::build_storage_key(&contract_address, &slot_key),
				&state_root.0,
				&non_existence.sibling_proofs,
			)
			.map_err(|e| PharosStateMachineError::SpvVerificationFailed(alloc::format!("{e:?}")))?;
			map.insert(key, None);
			continue;
		}

		// Otherwise verify existence proof
		let storage_proof_nodes = pharos_proof
			.storage_proof
			.get(slot_key.as_slice())
			.ok_or(PharosStateMachineError::MissingStorageProof)?;

		let storage_value = pharos_proof
			.storage_values
			.get(&slot_hash)
			.ok_or(PharosStateMachineError::MissingStorageValue)?;

		// Pad value to 32 bytes for proof verification
		let mut padded_value = [0u8; 32];
		if storage_value.len() <= 32 {
			padded_value[32 - storage_value.len()..].copy_from_slice(storage_value);
		} else {
			return Err(PharosStateMachineError::StorageValueTooLarge.into());
		}

		spv::verify_proof(
			storage_proof_nodes,
			&spv::build_storage_key(&contract_address, &slot_key),
			&padded_value,
			&state_root.0,
		)
		.map_err(|e| PharosStateMachineError::SpvVerificationFailed(alloc::format!("{e:?}")))?;

		map.insert(key, Some(storage_value.clone()));
	}

	Ok(map)
}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-104)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2))]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			message: GetRequestsWithProof,
		) -> DispatchResult {
			ensure_none(origin)?;

			Self::handle_get_requests(message).map_err(|err| {
				log::error!(target: "ismp", "pallet-coprocessor: {:?}", err);
				Error::<T>::HandlingError
			})?;

			Ok(())
		}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L62-153)
```rust
	pub fn handle_get_requests(
		GetRequestsWithProof { requests, source, response, address }: GetRequestsWithProof,
	) -> Result<(), Error> {
		// 1. Verify source proofs
		// 2. Extract fees
		// 3. Verify response proof
		// 4. insert GetResponse into mmr and request receipts
		// 5. emit Response events
		let host = <<T as Config>::IsmpHost>::default();

		// Reject duplicate requests within the batch.
		let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Get).collect();
		dedup_requests::<<T as Config>::IsmpHost>(&wrapped)?;

		for req in requests.iter() {
			let full = Request::Get(req.clone());

			// Get requests time out are relative to Hyperbridge
			if full.timed_out(host.timestamp()) {
				Err(Error::RequestTimeout { meta: full.clone().into() })?
			}

			// Source of the request must match the proof
			if full.source_chain() != source.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// Proof must come from the requested chain
			if full.dest_chain() != response.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// This request has already been responded to. Mirror `handlers/response.rs:61`:
			// dedup against `response_receipt`, which the dispatch path writes for this exact
			// GetRequest hash after producing a response. The receipt also binds the response
			// commitment, so external auditors can attest "Hyperbridge produced response X for
			// request Y" from one map.
			let probe = GetResponse { get: req.clone(), values: Default::default() };
			if host.response_receipt(&probe).is_some() {
				Err(Error::DuplicateResponse { meta: (&probe).into() })?
			}
		}

		// Ensure the proof height is equal to each retrieval height specified in the Get
		// requests
		if !requests.iter().all(|get| get.height == response.height.height) {
			Err(Error::InsufficientProofHeight)?
		}

		// Verify source proof
		let source_state_machine = validate_state_machine(&host, source.height)?;
		let state_root = host.state_machine_commitment(source.height)?;

		// Verify membership proof to ensure that requests where committed on source chain
		let commitments = requests
			.iter()
			.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
			.collect();
		source_state_machine.verify_membership(&host, commitments, state_root, &source)?;

		// Verify response proof
		let dest_state_machine = validate_state_machine(&host, response.height)?;
		let state_root = host.state_machine_commitment(response.height)?;

		// Insert GetResponses into mmr
		let mut responses = vec![];
		// Total payload bytes across this batch, used to mint reputation to
		// the relayer named in `address`. Each response contributes its
		// abi-encoded size — the same quantity the bandwidth gate charges —
		// so the mint stays proportional to the work paid for.
		let mut total_bytes: u32 = 0;
		for req in requests {
			let values: Vec<StorageValue> = dest_state_machine
				.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();

			let response = GetResponse { get: req, values };

			// Meter the app's bandwidth using the full size of the
			// abi-encoded GetResponse. Charged after proof verification
			// so the value sizes are final.
			let bytes = ismp::abi::encode_get_response(&response).len() as u32;
			<T as Config>::BandwidthGate::try_consume(
				&response.get.source,
				&response.get.from,
				bytes,
			)
			.map_err(|err| Error::Custom(alloc::format!("bandwidth gate: {err}")))?;
			total_bytes = total_bytes.saturating_add(bytes);

```

**File:** modules/pallets/call-decompressor/src/lib.rs (L218-253)
```rust
	/// - `compressed_bytes`: the compressed encoded runtime call represented in bytes.
	/// - `encoded_call_size`: the byte length of the decompressed encoded call.
	pub fn decompress(
		compressed_bytes: Vec<u8>,
		encoded_call_size: u32,
	) -> Result<Vec<u8>, DispatchError> {
		// Bound the claimed decompressed size against the configured maximum here,
		// at the single choke point every caller flows through. Previously this
		// gate lived only in `decompress_call` (the dispatch path); the unsigned
		// `validate_unsigned` mempool path called `decompress` directly with no
		// bound, so a fee-less attacker could claim `encoded_call_size = u32::MAX`
		// and have a tiny zstd "bomb" expanded to gigabytes during transaction-pool
		// validation, before any size check. Enforcing it here protects both paths.
		ensure!(encoded_call_size < T::MaxCallSize::get() * ONE_MB, Error::<T>::CallSizeOutOfBound);

		let mut decoder = StreamingDecoder::new(compressed_bytes.as_slice())
			.map_err(|_| Error::<T>::DecompressionFailed)?;

		let claimed = encoded_call_size as usize;
		let mut result = Vec::new();
		let mut chunk = vec![0u8; 4096];

		loop {
			let n = decoder.read(&mut chunk).map_err(|_| Error::<T>::DecompressionFailed)?;
			if n == 0 {
				break;
			}
			if result.len() + n > claimed {
				return Err(Error::<T>::DecompressionFailed.into());
			}
			result.extend_from_slice(&chunk[..n]);
		}

		ensure!(result.len() == claimed, Error::<T>::DecompressionFailed);

		Ok(result)
```

**File:** modules/consensus/pharos/primitives/src/spv.rs (L242-244)
```rust
	if proof_nodes.len() > MAX_PROOF_DEPTH {
		return Err(Error::ProofTooDeep);
	}
```
