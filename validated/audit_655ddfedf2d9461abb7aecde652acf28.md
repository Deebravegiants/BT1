### Title
Unbounded GET request `keys` array allows permanent freezing of escrowed relayer fees via gas/weight-limit DoS - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost.dispatch(DispatchGet)` and the corresponding Substrate `DispatchGet`/`GetRequest` path place no upper bound on the number of `keys` (or their combined size) that a caller can request in a single GET request. Because the entire batch of keys for one request must be verified and resolved atomically in a single transaction/extrinsic on both the source-proof and response-proof legs, an attacker can construct a GET request with enough keys to make that unavoidable, single, unsplittable proof-verification step exceed the destination chain's gas/weight limit — permanently preventing the request from ever being answered while the attacker's (or an innocent payer's) escrowed relayer fee remains locked and the request can never be resolved or refunded.

### Finding Description
`EvmHost.dispatch(DispatchGet)` accepts an arbitrary `bytes[] keys` array from `_msgSender()` with no length or aggregate-size check, escrows the fee, and commits the request: [1](#0-0) 

The equivalent Substrate-side `DispatchGet` (`modules/ismp/core/src/dispatcher.rs`) similarly has an unbounded `keys: Vec<Vec<u8>>` field with no cap: [2](#0-1) 

When the request is finally resolved (either via `pallet_state_coprocessor::handle_get_requests` when Hyperbridge is itself queried, or via `modules/ismp/core/src/handlers/response.rs` when a GET response for a request originating elsewhere is delivered), **all keys belonging to one GET request are verified and resolved in a single, unsplittable call** to `verify_state_proof`: [3](#0-2) [4](#0-3) 

The EVM state-machine's `verify_state_proof` groups keys by contract, decodes trie proofs, and walks every requested key inside one loop, with no per-request or per-batch key-count limit enforced anywhere before this point: [5](#0-4) 

I could not find any `MaxKeys`/length-cap constant, weight-metered per-key charge, or governance-configurable limit on `keys.length` anywhere in `modules/ismp/core`, `modules/pallets/state-coprocessor`, or `evm/src/core/EvmHost.sol` (confirmed via repo-wide search for `MaxKeys`, `max_keys`, `KeysExceed`, `MAX_KEYS` — no matches). This mirrors the referenced Ajna bug class exactly: a caller-controlled array length flows unchecked into a loop that must complete in a single atomic operation, and there is no mechanism to split or bound the work, so a sufficiently large array makes that operation permanently unexecutable within the block gas/weight limit.

### Impact Explanation
Because a GET request's proof verification for source membership and destination state-proof resolution must happen atomically for the whole key set (both in `handlers/response.rs::handle` and `state-coprocessor::handle_get_requests`), if the number/size of keys is large enough to push total execution beyond the block gas limit (EVM) or block weight limit (Substrate):
- The GET request can never be answered — `handleGetResponses`/`handle_get_requests` will always revert or fail to fit in a block.
- The relayer fee (`FeeMetadata.fee`) escrowed at dispatch time in `_requestCommitments[commitment]` is permanently unrecoverable, because there is no refund path for GET requests other than delivering a timeout, and the timeout-proof path (`handleGetRequestTimeouts`) is comparatively cheap per request but the underlying request itself can never be "answered" in the interim — more importantly, some fee/config paths (bandwidth metering, response minting) also assume the response can be produced, so a permanently-unprocessable request effectively locks funds and permanently blocks that request's lane.
- Because there's no fee scaling with `keys.length` on dispatch, the attacker pays the same fixed dispatch cost as a legitimate single-key request, making the attack cheap relative to the damage (bricking a specific request's response path and locking any escrowed relayer fee, or with fee = 0, spamming worthless-but-unprocessable requests that still consume attention/bandwidth-gate accounting on the coprocessor).

This satisfies the "permanent freezing of funds" / "route unable to deliver messages" bar for Medium/High severity.

### Likelihood Explanation
Likelihood is high: dispatching a GET request is fully permissionless — any contract or account can call `IDispatcher(host).dispatch(DispatchGet)` (EVM) or the Substrate `dispatch_request(DispatchRequest::Get(...))` entry point, supplying an arbitrarily large `keys` array, at negligible cost since neither the fee nor the dispatch-time gas cost scale meaningfully with `keys.length` (dispatch itself only allocates and emits an event — it does not touch the trie). The exploit requires no privileged position, no governance/collator compromise, and no special timing — a single transaction is sufficient to create an unprocessable, fee-locking request.

### Recommendation
- Enforce a hard cap on `keys.length` (and/or total encoded size of `keys`) in `EvmHost.dispatch(DispatchGet)` and in the Substrate `dispatch_request` path for `DispatchRequest::Get`, sized so that resolving the maximum allowed batch in one call is guaranteed to fit comfortably under the destination chain's gas/weight limit.
- Scale the required `fee` with `keys.length` / total key size so that verification cost is economically bounded and griefing is not free.
- Alternatively, redesign response delivery to allow chunked/incremental verification of a GET request's keys across multiple transactions/extrinsics rather than requiring the full set be resolved atomically.

### Proof of Concept
1. Attacker calls `IDispatcher(host).dispatch(DispatchGet{ dest, height, keys: <N very large 52-byte keys or a smaller N of keys pointing to different contracts>, timeout, fee: 0, context })` on the source `EvmHost`. Since `dispatch()` performs no length/size check, this succeeds and commits the request.
2. When a relayer/coprocessor attempts to resolve the response (`handle_get_requests` on Hyperbridge, or `handlers/response.rs::handle` when delivering to `HandlerV2.handleGetResponses`), `verify_state_proof` must process every one of the N keys, each requiring a proof-node decode/lookup, in a single call.
3. With N chosen large enough (attacker can determine the practical N off-chain by gas-profiling `verify_state_proof`/trie lookups), the call's gas/weight cost exceeds the block limit, so the transaction/extrinsic can never be included.
4. The GET request is now permanently unresolvable: no `GetResponse` can ever be produced, and any escrowed fee tied to `FeeMetadata` for that request's commitment remains locked with no way to force a resolution or refund outside of a timeout, and even the timeout path only refunds the fee (does not "fix" the DoS as a route-level issue if repeated), demonstrating a permanent-freeze / route-unable-to-deliver condition.

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

**File:** modules/ismp/core/src/dispatcher.rs (L38-53)
```rust
/// Simplified GET request, intended to be used for sending outgoing requests
#[derive(Clone)]
pub struct DispatchGet {
	/// The destination state machine of this request.
	pub dest: StateMachine,
	/// Module identifier of the sending module
	pub from: Vec<u8>,
	/// Raw Storage keys that would be used to fetch the values from the counterparty
	pub keys: Vec<Vec<u8>>,
	/// Height at which to read the state machine.
	pub height: u64,
	/// Some application-specific metadata relating to this request
	pub context: Vec<u8>,
	/// Relative from the current timestamp at which this request expires in seconds.
	pub timeout: u64,
}
```

**File:** modules/ismp/core/src/handlers/response.rs (L76-90)
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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L133-138)
```rust
		for req in requests {
			let values: Vec<StorageValue> = dest_state_machine
				.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();
```

**File:** modules/ismp/state-machines/evm/src/lib.rs (L149-245)
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
		// For keys that are 52 bytes we expect the first 20 bytes to be the contract address and
		// the last 32 bytes the slot hash.
		// For keys that are 20 bytes we expect that to the
		// contract or account address.
		// For keys that are 32 bytes we expect that to be a slothash in
		// the Ismp EVM host
		let contract_address = if key.len() == 52 {
			H160::from_slice(&key[..20])
		} else if key.len() == 32 {
			ismp_address
		} else if key.len() == 20 {
			contract_account_queries.push(H160::from_slice(&key));
			continue;
		} else {
			return Err(EvmStateMachineError::UnsupportedKeyLength.into());
		};
		let entry = contract_to_keys.entry(contract_address.0.to_vec()).or_insert(vec![]);

		let slot_hash = if key.len() == 52 {
			H::keccak256(&key[20..]).0.to_vec()
		} else {
			H::keccak256(&key).0.to_vec()
		};

		entry.push((key, slot_hash));
	}

	// The storage proof must correspond exactly to the contracts a key was requested from:
	// every one covered, and nothing else. Both directions are settled here, before a single
	// entry is resolved — resolving one clones the whole contract proof and rebuilds its trie,
	// so checking as we go would let a proof padded with unrequested accounts do that work
	// before being rejected, and would make which error surfaces depend on map ordering.
	// The honest prover already emits exactly this set, deriving its map from the requested
	// keys, so nothing legitimate is turned away.
	let result = contract_to_keys
		.clone()
		.into_keys()
		.all(|contract| evm_state_proof.storage_proof.contains_key(&contract));
	if !result {
		return Err(EvmStateMachineError::IncompleteStorageProof.into());
	}

	if evm_state_proof
		.storage_proof
		.keys()
		.any(|contract| !contract_to_keys.contains_key(contract))
	{
		return Err(EvmStateMachineError::UnrequestedContractProof.into());
	}

	for (contract_address, storage_proof) in evm_state_proof.storage_proof {
		// Unreachable: the correspondence check above already rejected any entry without a
		// requested key. Kept as a hard error rather than a skip so the invariant survives if
		// that check is ever moved or relaxed.
		let Some(keys) = contract_to_keys.remove(&contract_address) else {
			return Err(EvmStateMachineError::UnrequestedContractProof.into());
		};

		let contract_root = get_contract_account::<H>(
			evm_state_proof.contract_proof.clone(),
			&contract_address,
			root,
		)?
		.storage_root
		.0
		.into();

		let slot_hashes = keys.iter().map(|(_, slot_hash)| slot_hash.clone()).collect();
		let values = get_values_from_proof::<H>(slot_hashes, contract_root, storage_proof)?;
		keys.into_iter().zip(values).for_each(|((key, _), value)| {
			map.insert(key, value);
		});
	}
```
