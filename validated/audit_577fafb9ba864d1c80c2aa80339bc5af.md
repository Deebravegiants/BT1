### Title
Unbounded `GetRequest.keys` allows a single low-cost dispatch to force disproportionate, uncharged proof-verification work on Hyperbridge and relayers - ([File: modules/pallets/state-coprocessor/src/impls.rs])

### Summary
`DispatchGet`/`GetRequest` carries an attacker-controlled `keys: Vec<Vec<u8>>` with no length cap anywhere in the dispatch path (EVM `EvmHost.dispatch(DispatchGet)`, `pallet-ismp`'s `dispatch_request`, or the `GetRequest` router struct). The bandwidth/fee metering that is supposed to make the cost of a request proportional to its size is applied *after* the expensive multi-key state-proof verification work is already done, not before. This lets a single cheap request force a relayer/collator to do large, unbounded storage-proof verification work, and if the app has insufficient bandwidth credit the whole (already-computed) verification is thrown away when the bandwidth gate rejects it — a "pay a little, force a lot of expensive verification work" amplification pattern analogous to the in3-server signature-DDoS report (client forces expensive verification work on the network for a cost far below what the network incurs).

### Finding Description
`DispatchGet` (EVM: `evm/src/core/EvmHost.sol` `dispatch(DispatchGet memory get)`, Substrate: `modules/ismp/core/src/dispatcher.rs`) takes `bytes[] keys` / `Vec<Vec<u8>>` with **no bound on the number of keys**. Neither `EvmHost.dispatch` [1](#0-0)  nor `pallet-ismp`'s `dispatch_request` [2](#0-1)  validates or scales the fee/weight by `keys.length`. Per the SDK docs, the EVM host's per-byte fee model was explicitly removed, and only a flat, self-declared relayer `fee` remains — bandwidth is instead "pre-paid out-of-band" and metered by `pallet-bandwidth` [3](#0-2) .

When the GET request is fulfilled on Hyperbridge, `pallet_state_coprocessor::handle_get_requests` runs `verify_state_proof` against the *full, unbounded* `req.keys` for **every** request in the batch, and only **after** that expensive verification computes the response does it meter/gate bandwidth via `BandwidthGate::try_consume`: [4](#0-3) 

The comment even documents this ordering choice explicitly: "Meter the app's bandwidth using the full size of the abi-encoded GetResponse. Charged after proof verification so the value sizes are final." This means the (potentially very large) trie-proof verification cost for an arbitrary number of storage keys is *always paid for in full by the chain/relayer* regardless of whether the request should have been gated — the bandwidth check cannot prevent the expensive work, it can only reject the result afterward (`try_consume` failing simply errors the whole extrinsic out, discarding the verification work that was already performed). The generic `verify_state_proof` implementations used here (e.g. EVM state machine client) iterate per-key with no cap: [5](#0-4) , and the Substrate/EVM variant similarly loops unbounded over `keys` [6](#0-5) .

Additionally, `HandlerV2.handleGetResponses` on the EVM side dispatches an entire batch of `GetResponseLeaf`s and MMR-verifies them together with `Merkle` multi-proofs sized to `responsesLength`, with no cap on `message.responses.length` [7](#0-6) , compounding the same unbounded-batch pattern on the delivery side.

This differs from the in3-server bug only in the specific mechanism (unbounded signer list vs. unbounded key list), but the root cause class is identical: **an unprivileged caller can specify an arbitrarily large verification workload in a single cheap message, and the cost of verifying it is not charged upfront/proportionally to the party incurring the cost**, enabling amplified resource consumption relative to what the requester pays.

### Impact Explanation
This is a resource-exhaustion / DoS vector rather than a funds-theft bug, but it meets the "route unable to deliver messages" criterion in scope: an attacker can dispatch `GetRequest`s with pathologically large `keys` arrays cheaply (bounded only by calldata/extrinsic size limits, which are orders of magnitude larger than a reasonable per-request key count), forcing:
- Off-chain relayers/self-relayers to fetch and submit huge storage proofs for every key (`eth_getProof`/child-trie proofs), consuming their bandwidth/compute for near-zero attacker cost.
- Hyperbridge's `handle_get_requests`/`verify_state_proof` to perform O(n) trie-proof verification for arbitrary n before any bandwidth check can reject it, so the bandwidth gate provides no upfront protection against the compute cost, only against acceptance of the result.
- On EVM delivery, `handleGetResponses`/`handlePostRequests` batch verification scales with attacker-chosen batch size, similarly with no explicit cap.

Repeated/parallel submission of such requests can degrade throughput for legitimate relayers and Hyperbridge block execution, i.e., impede message delivery for the whole network — a scoped-in impact ("a route unable to deliver messages").

### Likelihood Explanation
Medium. Dispatching a `GetRequest`/`DispatchGet` requires no special privilege — any contract/account can call `IDispatcher.dispatch(DispatchGet)` or `pallet-ismp::dispatch_request` and can set `fee = 0` (self-relay) while filling `keys` with as many entries as calldata/extrinsic size limits allow. No code path inspects `keys.length` before performing/queueing the verification work, so triggering the disproportionate-cost condition needs no unusual conditions — just a request with many keys. The complicating factor for a full DoS is that the *attacker* must also arrange for someone (a relayer) to submit the proof for `handle_get_requests` to actually run the expensive path, but a malicious relayer/self-relayer colluding with the requester, or simply an attacker acting as their own relayer, achieves this trivially.

### Recommendation
- Enforce a hard cap on `GetRequest.keys.length` (and on `DispatchGet.keys.length`) at dispatch time, on both the EVM (`EvmHost.dispatch(DispatchGet)`) and Substrate (`pallet-ismp::dispatch_request`) entry points, rejecting requests that exceed a sane maximum key count.
- Similarly bound batch sizes accepted by `HandlerV2.handlePostRequests` / `handleGetResponses` and by `pallet_state_coprocessor::handle_get_requests` (`requests.len()`), independent of per-request key counts.
- Reorder the bandwidth/fee check in `handle_get_requests` so cost is estimated and gated *before* `verify_state_proof` is invoked (e.g., charge based on `keys.len()` upfront, then reconcile/adjust after verification if needed), so the expensive verification work cannot be performed for free when the app lacks bandwidth.
- Consider scaling the required relayer `fee`/weight with `keys.length` so verification cost is proportional to what the requester pays, mirroring the "limit signers, exclude irrelevant work" remediation from the referenced report.

### Proof of Concept
1. An attacker (no special role required) calls, on an EVM source chain:
```solidity
bytes[] memory keys = new bytes[](50_000); // near calldata size limit
for (uint i = 0; i < keys.length; i++) {
    keys[i] = abi.encodePacked(someContract, bytes32(i)); // 52-byte keys
}
DispatchGet memory get = DispatchGet({
    dest: someDestChain,
    height: 0,
    keys: keys,
    timeout: 0,
    fee: 0,           // self-relay, no fee required
    context: "",
    payer: address(this)
});
IDispatcher(host).dispatch(get); // evm/src/core/EvmHost.sol:974 — no cap on keys.length
```
2. The attacker (or a relayer they control) then relays this `GetRequest` plus a state proof for all 50,000 keys to Hyperbridge, invoking `pallet_state_coprocessor::handle_get_requests`.
3. `handle_get_requests` runs `dest_state_machine.verify_state_proof(&host, req.keys.clone(), ...)` over the full 50,000-key set (`modules/pallets/state-coprocessor/src/impls.rs:133-138`) — an expensive, unbounded operation — **before** `BandwidthGate::try_consume` is ever called (`impls.rs:142-151`).
4. If the app's bandwidth allowance is insufficient, `try_consume` errors out and the whole extrinsic fails, but the chain has already spent the compute verifying all 50,000 storage proofs, for an attacker who paid nothing beyond ordinary calldata/extrinsic fees.

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

**File:** modules/pallets/ismp/src/dispatcher.rs (L108-126)
```rust
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
```

**File:** sdk/packages/sdk/src/chains/evm.ts (L734-744)
```typescript
	/**
	 * Returns the protocol fee charged by the host on dispatch.
	 *
	 * The per-byte fee model was removed from `EvmHost`; on-chain dispatch
	 * now charges only the relayer fee carried in `DispatchPost.fee`.
	 * Bandwidth is pre-paid out-of-band via `BandwidthManager.purchase()`
	 * and metered on Hyperbridge by `pallet-bandwidth`.
	 */
	async quote(_request: IPostRequest | IGetRequest): Promise<bigint> {
		return 0n
	}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L133-152)
```rust
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

**File:** modules/ismp/state-machines/evm/src/lib.rs (L149-198)
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

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```
