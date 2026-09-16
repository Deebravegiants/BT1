Based on the investigation, I have enough evidence to construct a valid analog for the GET-request `keys` field.

### Title
Unbounded `GetRequest.keys` array allows a single dispatch to force unbounded state-proof verification work at fixed weight - (File: `modules/ismp/core/src/router.rs`, `modules/ismp/core/src/handlers/response.rs`, `modules/pallets/state-coprocessor/src/impls.rs`)

### Summary
`GetRequest`/`DispatchGet` carries `keys: Vec<Vec<u8>>` with no on-chain bound on the number of keys or their sizes. [1](#0-0) 
Any unprivileged module/pallet that calls `IsmpDispatcher::dispatch_request(DispatchRequest::Get(...))` can submit an arbitrarily large `keys` vector, and downstream verification/response code (`verify_state_proof`, `verify_non_membership`, and the relayer's `handle_unsigned`/`handle_get_requests` path) iterates over every key with no cap, mirroring the ink! "unbounded vector decode" bug class where a single unbounded collection blows past intended resource limits.

### Finding Description
`GetRequest.keys` and `DispatchGet.keys` are plain, unbounded `Vec<Vec<u8>>` fields: [2](#0-1) 

The response handler iterates `request.keys.clone()` directly into `verify_state_proof` with no length or size ceiling: [3](#0-2) 

The Substrate state-machine implementation of `verify_state_proof`/`verify_non_membership` walks the trie once per key with no bound check before doing the work: [4](#0-3) 

The unsigned `handle_get_requests` path in `pallet-state-coprocessor`, which is reachable via `ValidateUnsigned::validate_unsigned` for any relayer-submitted unsigned extrinsic carrying a `GetRequestsWithProof`, also loops over `req.keys.clone()` per request with no cap before minting relayer reputation and consuming bandwidth: [5](#0-4) [6](#0-5) 

The originating dispatch calls that let a user/app populate this field are also charged flat, non-parametrized weights instead of weight proportional to `keys.len()`. The example demo pallet illustrates the pattern verbatim — `get_request` charges a fixed `Weight::from_parts(1_000_000, 0)` regardless of the `params.keys: Vec<Vec<u8>>` length: [7](#0-6) [8](#0-7) 

No bound type (`BoundedVec<Vec<u8>, ConstU32<N>>` or similar) or explicit `ensure!(keys.len() <= MAX)` check exists anywhere in the `GetRequest`/`DispatchGet`/`verify_state_proof` call chain (confirmed by exhaustive search — no `MaxKeys`, `MaxStateMachineKeys`, or `keys.len() >` guard exists in the codebase).

### Impact Explanation
An unprivileged application pallet (any pallet implementing `IsmpModule`/calling the dispatcher, or any relayer submitting a `ResponseMessage`/`GetRequestsWithProof`) can construct a `GetRequest` with an unbounded number of keys (or unbounded-size individual keys). This causes:
- Unbounded trie lookups per block in `verify_state_proof`/`verify_non_membership`, charged at a flat weight that does not scale with the actual number of keys, letting an attacker consume disproportionate block execution time relative to the fee/weight paid — a resource-exhaustion vector against block production (a form of route/liveness denial, matching the "route unable to deliver messages" acceptance criterion since a validator/collator could stall block execution processing an oversized batch).
- Unbounded storage-proof sizes passed through the relayer path and stored/committed via MMR/offchain leaf storage, inflating proof sizes without limit, similar to how the ink! bug caused unbounded decode buffers to overflow fixed capacity, except here it manifests as unbounded weight/computation rather than a hard decode-size ceiling.

This is a resource/DoS-class issue tied to weight-metering soundness rather than a direct fund-theft/mint bug, so it is Medium severity under the reachable-analog criteria (a route becoming unable to deliver/process messages during an attack window).

### Likelihood Explanation
Likelihood is high in terms of reachability — `dispatch_request` with `DispatchRequest::Get` is a standard, documented, permissionless integration point for any application pallet, and the relayer-facing `handle_unsigned`/`ResponseMessage` paths accept attacker-influenced `GetRequest.keys` from the original dispatcher. However, exploiting it to meaningfully degrade block production requires the attacker to also pay dispatch fees proportional to message count (not to key count within a single message), which somewhat limits the economic cost calculus but does not eliminate the underlying missing bound.

### Recommendation
Introduce an explicit, enforced bound on `GetRequest.keys`/`DispatchGet.keys` (e.g., convert to `BoundedVec<Vec<u8>, T::MaxKeys>` or add `ensure!(keys.len() <= T::MaxKeys::get(), Error::TooManyKeys)` at dispatch time in `pallet_ismp::Pallet::dispatch_request`), and mirror the same check in `verify_state_proof`/`verify_non_membership` before executing any trie lookups. Weight annotations for extrinsics that embed a `keys: Vec<Vec<u8>>` (e.g. the pattern in `modules/pallets/demo/src/lib.rs::get_request`) should be parametrized on `keys.len()` rather than using a flat constant.

### Proof of Concept
Conceptual (no local test harness available to execute, but derivable directly from the code above):
1. A malicious application pallet calls `T::IsmpHost::dispatch_request(DispatchRequest::Get(DispatchGet { keys: vec![vec![0u8; 32]; N], .. }), fee)` with `N` set to a very large number (e.g., 100,000+), paying only the flat weight charged by its own extrinsic (as in `modules/pallets/demo/src/lib.rs::get_request`, which charges `Weight::from_parts(1_000_000, 0)` irrespective of `params.keys.len()`).
2. `pallet_ismp::Pallet::<T>::dispatch_request` stores this request without any check on `keys.len()` [9](#0-8) .
3. When a relayer later submits the corresponding `ResponseMessage`/`GetRequestsWithProof`, `handle`/`handle_get_requests` iterates `request.keys.clone()` through `verify_state_proof`, performing N trie lookups [3](#0-2) , with no per-request cap, disproportionately consuming block weight/time relative to what was charged at dispatch.

### Citations

**File:** modules/ismp/core/src/router.rs (L100-128)
```rust
)]
pub struct GetRequest {
	/// The source state machine of this request.
	#[serde(with = "serde_hex_utils::as_string")]
	pub source: StateMachine,
	/// The destination state machine of this request.
	#[serde(with = "serde_hex_utils::as_string")]
	pub dest: StateMachine,
	/// The nonce of this request on the source chain
	pub nonce: u64,
	/// Module identifier of the sending module
	#[serde(with = "serde_hex_utils::as_hex")]
	pub from: Vec<u8>,
	/// Raw Storage keys that would be used to fetch the values from the counterparty
	/// For deriving storage keys for ink contract fields follow the guide in the link below
	/// `<https://use.ink/datastructures/storage-in-metadata#a-full-example>`
	/// Substrate Keys
	/// The algorithms for calculating raw storage keys for different substrate pallet storage
	/// types are described in the following links
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/map.rs#L34-L42>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/double_map.rs#L34-L44>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/nmap.rs#L39-L48>`
	/// `<https://github.com/paritytech/substrate/blob/master/frame/support/src/storage/types/value.rs#L37>`
	/// EVM Keys
	/// For fetching keys from EVM contracts each key should either be 52 bytes or 20 bytes
	/// For 52 byte keys we expect it to be a concatenation of contract address and slot hash
	/// For 20 bytes we expect it to be a contract or account address
	#[serde(with = "serde_hex_utils::seq_of_hex")]
	pub keys: Vec<Vec<u8>>,
```

**File:** modules/ismp/core/src/handlers/response.rs (L76-89)
```rust
	// Since each get request can contain multiple storage keys
	// we should handle them individually
	let result = msg
		.requests
		.iter()
		.cloned()
		.map(|request| {
			let wrapped_req = Request::Get(request.clone());
			let keys = request.keys.clone();
			let values = state_machine
				.verify_state_proof(host, keys, state.state_root, &proof)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L240-280)
```rust
	fn verify_state_proof(
		&self,
		_host: &dyn IsmpHost,
		keys: Vec<Vec<u8>>,
		root: H256,
		proof: &Proof,
	) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
		// The trie root is supplied by the caller, bound to the calling context, so a relayer
		// cannot steer verification at the wrong trie.
		let StateMachineProof { hasher, storage_proof } =
			codec::Decode::decode(&mut &*proof.proof)
				.map_err(SubstrateStateMachineError::ProofDecodeError)?;
		let data = match hasher {
			HashAlgorithm::Keccak => {
				let db = StorageProof::new(storage_proof).into_memory_db::<Keccak256>();
				let trie = TrieDBBuilder::<LayoutV0<Keccak256>>::new(&db, &root).build();
				keys.into_iter()
					.map(|key| {
						let value = trie
							.get(&key)
							.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
						Ok::<_, SubstrateStateMachineError>((key, value))
					})
					.collect::<Result<BTreeMap<_, _>, _>>()?
			},
			HashAlgorithm::Blake2 => {
				let db = StorageProof::new(storage_proof).into_memory_db::<BlakeTwo256>();
				let trie = TrieDBBuilder::<LayoutV0<BlakeTwo256>>::new(&db, &root).build();
				keys.into_iter()
					.map(|key| {
						let value = trie
							.get(&key)
							.map_err(|e| SubstrateStateMachineError::TrieError(format!("{e:?}")))?;
						Ok::<_, SubstrateStateMachineError>((key, value))
					})
					.collect::<Result<BTreeMap<_, _>, _>>()?
			},
		};

		Ok(data)
	}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L130-155)
```rust
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

			responses.push(response);
		}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L121-129)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}
```

**File:** modules/pallets/demo/src/lib.rs (L187-214)
```rust
		#[pallet::weight(Weight::from_parts(1_000_000, 0))]
		#[pallet::call_index(1)]
		pub fn get_request(origin: OriginFor<T>, params: GetRequest) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let dest = match <T as pallet_ismp::Config>::HostStateMachine::get() {
				StateMachine::Kusama(_) => StateMachine::Kusama(params.para_id),
				StateMachine::Polkadot(_) => StateMachine::Polkadot(params.para_id),
				_ => Err(DispatchError::Other("Pallet only supports parachain hosts"))?,
			};

			let get = DispatchGet {
				dest,
				from: PALLET_ID.to_bytes(),
				keys: params.keys,
				height: params.height as u64,
				timeout: params.timeout,
				context: Default::default(),
			};

			let dispatcher = T::IsmpHost::default();
			dispatcher
				.dispatch_request(
					DispatchRequest::Get(get),
					FeeMetadata { payer: origin, fee: Default::default() },
				)
				.map_err(|_| Error::<T>::GetDispatchFailed)?;
			Ok(())
		}
```

**File:** modules/pallets/demo/src/lib.rs (L293-302)
```rust
	pub struct GetRequest {
		/// Destination parachain
		pub para_id: u32,
		/// Height at which to read state
		pub height: u32,
		/// request timeout
		pub timeout: u64,
		/// Storage keys to read
		pub keys: Vec<Vec<u8>>,
	}
```

**File:** modules/pallets/ismp/src/impls.rs (L89-121)
```rust
	/// Dispatch an outgoing request, returns the request commitment
	pub fn dispatch_request(request: Request, meta: FeeMetadata<T>) -> Result<H256, ismp::Error> {
		let commitment = hash_request::<Pallet<T>>(&request);

		if RequestCommitments::<T>::contains_key(commitment) {
			Err(ismp::Error::Custom("Duplicate request".to_string()))?
		}

		let (dest_chain, source_chain, nonce) =
			(request.dest_chain(), request.source_chain(), request.nonce());
		let leaf_index_and_pos = T::OffchainDB::push(Leaf::Request(request));
		// Deposit Event
		Pallet::<T>::deposit_event(Event::Request {
			request_nonce: nonce,
			source_chain,
			dest_chain,
			commitment,
		});

		RequestCommitments::<T>::insert(
			commitment,
			RequestMetadata {
				offchain: LeafIndexAndPos {
					leaf_index: leaf_index_and_pos.index,
					pos: leaf_index_and_pos.position,
				},
				fee: meta,
				claimed: false,
			},
		);

		Ok(commitment)
	}
```
