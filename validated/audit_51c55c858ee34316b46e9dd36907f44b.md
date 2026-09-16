Confirmed: nowhere along `dispatch_request` (Rust, `modules/pallets/ismp/src/dispatcher.rs:92-152`), `dispatch(DispatchGet)` (Solidity, `evm/src/core/EvmHost.sol:974-1013`), or any `verify_state_proof`/`get_values_from_proof` implementation is there a cap on `keys.len()`. Fee is a flat, caller-chosen amount independent of `keys.length` (confirmed by the SDK comment noting the per-byte fee model was removed), so an attacker pays a fixed cost regardless of how many keys they attach.

### Title
Unbounded `keys` array in `DispatchGet`/GET requests enables cheap, permanent griefing of the GET-request delivery pipeline - (File: `evm/src/core/EvmHost.sol`, `modules/pallets/ismp/src/dispatcher.rs`, `modules/ismp/state-machines/evm/src/lib.rs`)

### Summary
Any unprivileged caller can dispatch a `GetRequest`/`DispatchGet` with an arbitrarily large `keys: Vec<Vec<u8>>`/`bytes[] keys` array for a fixed, size-independent relayer fee. Every downstream step that must process this request — the coprocessor's `verify_state_proof` per-state-machine implementations, `get_values_from_proof`, and the destination-side proof construction — contains an unbounded `for key in keys` loop with no upper bound check, mirroring the `ERC721Pool` pattern of unbounded loops over caller-supplied array length.

### Finding Description
`EvmHost.dispatch(DispatchGet memory get)` (`evm/src/core/EvmHost.sol:974-1013`) accepts `get.keys` of unbounded length and stores the request with only a flat `FeeMetadata({sender, fee: get.fee})` — the fee is not scaled to `keys.length` in any way. The same is true on the Substrate side: `pallet_ismp::dispatcher::dispatch_request` (`modules/pallets/ismp/src/dispatcher.rs:92-152`) copies `dispatch_get.keys` verbatim into the `GetRequest` with no length validation, and the flat fee is collected via `T::Currency::transfer` regardless of key count. [1](#0-0) [2](#0-1) 

When the request is later resolved (by `pallet-state-coprocessor::handle_get_requests` or by a destination state-machine client verifying the response), every `verify_state_proof` implementation iterates once per key with no bound: e.g. `modules/ismp/state-machines/evm/src/lib.rs:149-261` groups and resolves every key in `keys`, and the underlying trie lookup `get_values_from_proof` (`modules/ismp/state-machines/evm/src/utils.rs:182-198`) loops `for key in keys { trie.get(&key) }` unconditionally. [3](#0-2) [4](#0-3) 

The same unbounded per-key loop pattern recurs in every other `verify_state_proof` implementation (`substrate_evm.rs:182-248`, `tendermint.rs:241-349`, `pharos/src/lib.rs:178-336`, `substrate/src/lib.rs:240-280`), meaning no state-machine backend enforces a maximum `keys.length`. [5](#0-4) 

### Impact Explanation
An attacker can dispatch a single `GetRequest` with a huge `keys` array (e.g. tens of thousands of entries) for the same flat fee as a one-key request. This request becomes a poison pill for the delivery pipeline:
- Any relayer/coprocessor attempting to construct or verify the state proof for this request must resolve every key, which, given the size-independent fee, is economically irrational or computationally/weight-prohibitive to complete, especially since Substrate extrinsics like `handle_unsigned` (`modules/pallets/ismp/src/lib.rs:373-382`) are weight-metered and could exceed block weight limits when processing such a request bundled with others.
- On the EVM destination side, delivering the corresponding `GetResponse` via `HandlerV2.handleGetResponses` still requires the relayer to have assembled a valid proof/response for every key; a sufficiently large key set makes constructing a response that fits under the destination chain's block gas limit impossible, permanently stranding the request (and any escrowed relayer fee) as neither deliverable nor cheaply timeout-able at scale, echoing the "NFT pools with a large subset of tokens will not be created" impact from the source report — here it's "GET requests with a large subset of keys will never be delivered," permanently blocking that message and freezing its escrowed fee.

### Likelihood Explanation
High likelihood: this requires only a single, permissionless `dispatch(DispatchGet)`/`dispatch_request` call from any account, with no privileged role, no governance action, and no cooperation from other parties. The fee is fixed and does not scale with array size, so the attack is cheap to execute.

### Recommendation
Enforce a maximum `keys.length` (and/or a fee proportional to `keys.length`) at dispatch time in both `EvmHost.dispatch(DispatchGet)` and `pallet_ismp::dispatch_request`, rejecting `DispatchGet`/`GetRequest`s whose key count exceeds a protocol-defined bound so that every downstream `verify_state_proof` loop is guaranteed to complete within available gas/weight budgets.

### Proof of Concept
1. Call `EvmHost.dispatch(DispatchGet)` (or the Substrate `dispatch_request(DispatchRequest::Get(...))` equivalent) with `keys` containing, e.g., 50,000 arbitrary 32-byte entries and the minimum non-zero `fee`.
2. Observe that `_requestCommitments[commitment]` is stored with the attacker-chosen flat fee, unrelated to `keys.length` (`evm/src/core/EvmHost.sol:1000-1001`).
3. Attempt to resolve this request through `pallet_state_coprocessor::handle_get_requests` or the destination `verify_state_proof` path; observe the unbounded per-key loop (`get_values_from_proof`, `modules/ismp/state-machines/evm/src/utils.rs:190-195`) scales linearly with the attacker-supplied `keys.length`, exceeding practical gas/weight limits and leaving the request permanently undeliverable while its escrowed fee remains locked.

### Citations

**File:** evm/src/core/EvmHost.sol (L974-1013)
```text
    function dispatch(DispatchGet memory get) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                get.fee, path, address(this), block.timestamp
            );
        } else if (get.fee > 0) {
            IERC20(feeToken()).safeTransferFrom(_msgSender(), address(this), get.fee);
        }

        uint64 timeoutTimestamp = get.timeout == 0 ? 0 : uint64(block.timestamp) + uint64(get.timeout);
        GetRequest memory request = GetRequest({
            source: host(),
            dest: get.dest,
            nonce: uint64(_nextNonce()),
            from: abi.encodePacked(_msgSender()),
            timeoutTimestamp: timeoutTimestamp,
            keys: get.keys,
            height: get.height,
            context: get.context
        });

        // make the commitment
        commitment = request.hash();
        _requestCommitments[commitment] = FeeMetadata({sender: _msgSender(), fee: get.fee});
        emit GetRequestEvent({
            source: string(request.source),
            dest: string(request.dest),
            from: request.from,
            keys: request.keys,
            nonce: request.nonce,
            height: request.height,
            context: request.context,
            timeoutTimestamp: request.timeoutTimestamp,
            fee: get.fee
        });
    }
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-151)
```rust
	fn dispatch_request(
		&self,
		request: DispatchRequest,
		fee: FeeMetadata<T>,
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}

		let request = match request {
			DispatchRequest::Get(dispatch_get) => {
				let get = GetRequest {
					source: self.host_state_machine(),
					dest: dispatch_get.dest,
					nonce: self.next_nonce(),
					from: dispatch_get.from,
					keys: dispatch_get.keys,
					height: dispatch_get.height,
					context: dispatch_get.context,
					timeout_timestamp: if dispatch_get.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_get.timeout)
					},
				};
				Request::Get(get)
			},
			DispatchRequest::Post(dispatch_post) => {
				let post = PostRequest {
					source: self.host_state_machine(),
					dest: dispatch_post.dest,
					nonce: self.next_nonce(),
					from: dispatch_post.from,
					to: dispatch_post.to,
					timeout_timestamp: if dispatch_post.timeout == 0 {
						0
					} else {
						<T::TimestampProvider as UnixTime>::now()
							.as_secs()
							.saturating_add(dispatch_post.timeout)
					},
					body: dispatch_post.body,
				};
				Request::Post(post)
			},
		};

		let commitment = Pallet::<T>::dispatch_request(request, fee)?;

		Ok(commitment)
	}
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L149-172)
```rust
pub fn verify_state_proof<H: Keccak256 + Send + Sync>(
	keys: Vec<Vec<u8>>,
	root: H256,
	proof: &Proof,
	ismp_address: H160,
) -> Result<BTreeMap<Vec<u8>, Option<Vec<u8>>>, Error> {
	// Reject repeats before doing any work at all. They are already an error — repeats collapse
	// in the map returned below, so the caller's key-count check fails — but reaching that
	// check means every repeat has been verified first, and for account queries that is a
	// clone of the whole contract proof each time.
	let mut seen_keys = BTreeSet::new();
	for key in &keys {
		if !seen_keys.insert(key.as_slice()) {
			return Err(EvmStateMachineError::DuplicateKey.into());
		}
	}

	let evm_state_proof = decode_evm_state_proof(proof)?;
	let mut map = BTreeMap::new();
	let mut contract_to_keys = BTreeMap::new();
	let mut contract_account_queries = Vec::new();

	// Group keys by the contract address they belong to
	for key in keys {
```

**File:** modules/ismp/state-machines/evm/src/utils.rs (L182-198)
```rust
pub fn get_values_from_proof<H: Keccak256 + Send + Sync>(
	keys: Vec<Vec<u8>>,
	root: H256,
	proof: Vec<Vec<u8>>,
) -> Result<Vec<Option<DBValue>>, Error> {
	let mut values = vec![];
	let proof_db = StorageProof::new(proof).into_memory_db::<KeccakHasher<H>>();
	let trie = TrieDBBuilder::<EIP1186Layout<KeccakHasher<H>>>::new(&proof_db, &root).build();
	for key in keys {
		let val = trie
			.get(&key)
			.map_err(|e| EvmStateMachineError::TrieReadError(format!("{e:?}")))?;
		values.push(val);
	}

	Ok(values)
}
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
