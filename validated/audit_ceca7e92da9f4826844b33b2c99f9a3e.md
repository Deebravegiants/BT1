### Title
Unbounded `keys` array in `GetRequest`/`DispatchGet` allows a single dispatcher to force unbounded, unsplittable state-proof verification work, permanently DoSing GET-response delivery - (File: modules/pallets/state-coprocessor/src/impls.rs)

### Summary
`DispatchGet`/`GetRequest` carries an arbitrary-length `keys: Vec<Vec<u8>>` with no upper bound enforced anywhere in the dispatch path (`modules/ismp/core/src/dispatcher.rs`, `evm/src/core/EvmHost.sol::dispatch(DispatchGet)`). Unlike POST requests — where a relayer chooses how many requests to pack into one `handlePostRequests`/`RequestMessage` batch, and can always shrink the batch to fit a block — a single `GetRequest`'s response must be produced and verified as one atomic unit tied to that request's commitment. This mirrors the reNFT bug class: an attacker-controlled, unbounded collection forces a single unsplittable operation whose cost scales with attacker-chosen size, risking exceeding the resource limit of the chain that must process it.

### Finding Description
`pallet_state_coprocessor::handle_get_requests` (`modules/pallets/state-coprocessor/src/impls.rs`) iterates every `GetRequest` in the batch and, per request, calls `dest_state_machine.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?` for the *entire* `req.keys` set in one call: [1](#0-0) 

Critically, the bandwidth gate (`BandwidthGate::try_consume`), which is the only sender-side cost/allowance check, is invoked **after** this proof verification has already been performed, as the code comment explicitly states ("Charged after proof verification so the value sizes are final"): [2](#0-1) 

The `keys` field itself has no size cap in the request type: [3](#0-2) 

and the EVM dispatch entrypoint accepts `get.keys` unchecked before committing the request: [4](#0-3) 

Because the response for a `GetRequest` is bound to a single request commitment (hash of the whole `GetRequest`, including all its keys), the relayer/coprocessor cannot split one request's key set across multiple extrinsics the way `handlePostRequests` batches can be resized — the proof for all keys in that request must be verified together in a single unsigned extrinsic call to produce one `GetResponse`.

### Impact Explanation
An unprivileged application (or attacker acting as an "app") can dispatch a single `GetRequest`/`DispatchGet` with an extremely large number of storage `keys`. When Hyperbridge's coprocessor attempts to answer it, `verify_state_proof` must walk/verify a trie multiproof across all requested keys in one call — cost that grows with the attacker-chosen key count and is not bounded ahead of time. If this exceeds the Substrate block weight/proof-size limit for the unsigned `handle_get_requests` extrinsic, the extrinsic can never be included in a block, so:
- The `GetResponse` can never be produced/delivered, leaving the request permanently pending (a route unable to deliver messages, matching the report's "stuck order" condition).
- Any relayer fee escrowed for the request (`FeeMetadata.fee`) is permanently locked, since it can only be reclaimed via a timeout path that itself does not depend on this over-large proof, but the app's expected response/business logic waiting on `onGetResponse` never fires — a permanent freeze of the request lifecycle analogous to the reNFT rental order that can never be `stopRent`-ed.
- Because the bandwidth gate check happens only after the expensive proof verification, an app with zero paid bandwidth can still repeatedly trigger this expensive, unsplittable verification work, amplifying the DoS/resource-exhaustion risk against the shared coprocessor extrinsic used by all GET requests.

### Likelihood Explanation
Any application/user with access to `IDispatcher.dispatch(DispatchGet)` on any connected EVM chain (or the equivalent Substrate `dispatch_request(DispatchRequest::Get(...))`) can construct such a request without needing elevated privileges, a large payment, or dependency on state layout of the target chain (arbitrary garbage keys are sufficient to inflate `keys.len()`; failed/garbage keys still cost membership verification work). No cap on `keys.length` exists in the Solidity interface, docs, or the Rust dispatcher/handler code inspected. This makes the trigger straightforward, though the precise threshold at which `verify_state_proof` cost exceeds the coprocessor's block weight limit was not directly measured from the index (see Uncertainty below).

### Recommendation
- Enforce a maximum number of `keys` (and/or maximum aggregate key bytes) per `GetRequest` at dispatch time, both in `EvmHost.sol::dispatch(DispatchGet)` and in the Substrate `dispatch_request` path (`modules/ismp/core/src/dispatcher.rs`), rejecting requests that exceed the cap before a commitment is stored.
- Move/duplicate the `BandwidthGate::try_consume` check to run **before** `verify_state_proof` in `pallet_state_coprocessor::handle_get_requests` (estimate cost from the request's own `keys`/`context` sizes, which are already used for that formula), so unpaid/underfunded apps cannot force expensive proof verification to run at all.
- Alternatively, weight-meter `handle_get_requests` proportionally to `keys.len()` summed over the batch and reject/split extrinsics whose declared weight would exceed the configured block weight limit.

### Proof of Concept
Conceptual PoC (mirrors the external report's structure):
1. Deploy/find an application allowed to call `IDispatcher(host).dispatch(DispatchGet)` on an EVM chain connected to Hyperbridge.
2. Construct a `DispatchGet` with `keys` containing tens of thousands of distinct 52-byte storage keys (or 20-byte account keys) targeting arbitrary/garbage addresses — no special access or high fee required since the bandwidth check occurs after proof verification.
3. Submit `dispatch(get)`; the request commitment is stored and the event emitted regardless of key count (`evm/src/core/EvmHost.sol:974-1013`).
4. A relayer/coprocessor later attempts to answer it via `pallet_state_coprocessor::handle_get_requests`, which must call `verify_state_proof` over the full key set in one call (`modules/pallets/state-coprocessor/src/impls.rs:133-139`) before any bandwidth check.
5. If the resulting proof-verification workload exceeds the coprocessor chain's per-extrinsic/block weight (or proof-size) limit, the unsigned extrinsic can never be finalized, permanently blocking the `GetResponse` for that request — analogous to `Stop::stopRent()` exceeding the block gas limit in the source report.

**Uncertainty**: I could not directly locate the exact weight declaration/`#[pallet::weight(...)]` metadata or benchmarked per-key cost for `handle_get_requests`/`verify_state_proof` in the indexed content, nor a definitive numeric threshold at which this would exceed a block's weight limit — the index may not include the full weight/benchmarking files. This should be verified by inspecting the coprocessor's dispatch weight declaration and the trie-proof verifier's per-key cost in a full checkout before treating the severity as confirmed at Medium/High rather than only theoretical.

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L133-139)
```rust
		for req in requests {
			let values: Vec<StorageValue> = dest_state_machine
				.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();

```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L140-152)
```rust
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
