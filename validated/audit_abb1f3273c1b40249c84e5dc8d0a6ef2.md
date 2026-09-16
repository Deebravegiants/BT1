### Title
Bandwidth allowance checked after, not before, expensive state-proof verification in GET request processing - allows unpenalized DoS via `pallet-state-coprocessor::handle_unsigned` - (File: modules/pallets/state-coprocessor/src/impls.rs)

### Summary
`pallet-state-coprocessor::handle_get_requests` performs full Merkle/state-trie proof verification for a batch of `GetRequest`s (`verify_membership`, `verify_state_proof`) before the `BandwidthGate::try_consume` allowance check for the request's source app. Because this pallet call is submitted as an **unsigned extrinsic** (free, no fee, checked by `ValidateUnsigned`), an app with zero bandwidth allowance — or an attacker who dispatches cheap, fee-free `GET` requests from a contract they control — can force the network to perform the full cryptographic verification workload for large batches of storage keys, repeatedly, before the request is ultimately rejected for insufficient bandwidth. This is directly analogous to the reported "Oracle requests without financial penalties" bug class: requests are accepted and processed at cost to the network before the requester is charged/validated, and there is no requirement to "follow through" or pay before the expensive work is done.

### Finding Description
GET requests are dispatched permissionlessly and cheaply: `EvmHost.dispatch(DispatchGet)` and `pallet_ismp::Pallet::dispatch_request` only require a fee if the app wants relayer delivery — `fee` can legitimately be `0` for self-relay [1](#0-0) , and the equivalent Substrate dispatcher path also allows `fee: Zero::zero()` with no bandwidth check performed at dispatch time [2](#0-1) .

There is no bandwidth gate enforcement on the dispatch of GET requests themselves. The `BandwidthGate` is only invoked in two places: (1) `on_accept` for POST requests [3](#0-2) , and (2) inside `pallet_state_coprocessor::handle_get_requests`, per-response, **after** the expensive state proof has already been computed:

```
for req in requests {
    let values: Vec<StorageValue> = dest_state_machine
        .verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
        ...
    let response = GetResponse { get: req, values };
    let bytes = ismp::abi::encode_get_response(&response).len() as u32;
    <T as Config>::BandwidthGate::try_consume(&response.get.source, &response.get.from, bytes)
        .map_err(...)?;
``` [4](#0-3) 

The costly `verify_state_proof` call (Merkle/trie proof verification against the destination chain's state root) executes unconditionally for every request in the batch, and only after this work is done does the pallet check whether the requesting app (`response.get.source`, `response.get.from`) has any bandwidth allowance at all. If it doesn't, the whole extrinsic reverts with a bandwidth-gate error, but the verification work has already consumed block weight/CPU.

Crucially, this call path is exposed as a **free, unsigned extrinsic**:
```
pub fn handle_unsigned(origin: OriginFor<T>, message: GetRequestsWithProof) -> DispatchResult {
    ensure_none(origin)?;
    Self::handle_get_requests(message)...
}
``` [5](#0-4) 

and its `ValidateUnsigned::validate_unsigned` implementation calls the exact same `handle_get_requests` function (including the full proof-verification path) just to admit the transaction into the mempool:
```
fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
    let Call::handle_unsigned { message } = call else { ... };
    if let Err(err) = Self::handle_get_requests(message.clone()) {
        ...
        return Err(...);
    }
    ...
}
``` [6](#0-5) 

This means the expensive verification (including `verify_state_proof`) runs **twice per submission** — once during mempool validation on every peer that receives the gossiped transaction, and again on execution — with no fee, no stake, and no upfront bandwidth requirement, exactly mirroring the reported pattern of "users submit requests without providing the required on-chain follow-through/payment, incurring no cost while occupying resources."

Additionally, `GetRequestsWithProof.requests` is an unbounded `Vec<GetRequest>` [7](#0-6) , and each `GetRequest.keys` is likewise an unbounded `Vec<Vec<u8>>` — no batch-size cap was found guarding the number of keys/requests processed before the bandwidth check, so an attacker can maximize the free verification workload per submission.

### Impact Explanation
This enables a low-cost, network-wide denial-of-service: an attacker (who can be their own "relayer" for a self-controlled app with no bandwidth allowance) repeatedly submits `handle_unsigned` transactions with large batches of `GetRequest`s and valid state/membership proofs. Every full node performing transaction-pool validation, and every collator/validator executing the block, pays the full cost of trie/Merkle proof verification for the entire batch before the bandwidth gate rejects it. Because the extrinsic is unsigned, there is no transaction fee and no bandwidth pre-payment gating this work, so the attacker incurs none of the compute cost while imposing it broadly on the network — a classic "route unable to deliver messages" / availability degradation for legitimate relayers and applications trying to get their own GET responses processed, and a direct DoS risk to Hyperbridge's consensus-critical unsigned-extrinsic pool.

### Likelihood Explanation
High. The attack requires only: (a) dispatching a `GetRequest` (or batch) from a contract without a bandwidth subscription (or after it's allowlisted but later revoked/expired) — cheap and unrestricted, since GET dispatch performs no bandwidth check; and (b) constructing a real state/membership proof for those keys, which is off-chain and reusable across many submissions since duplicate rejection only occurs after processing. The `handle_unsigned`/`validate_unsigned` pattern is explicitly designed to let "anyone execute ISMP messages for free provided they have valid proofs," which is precisely the mechanism abused here since the payment/allowance check is misordered relative to the expensive verification step.

### Recommendation
Move the `BandwidthGate::try_consume` check (or an equivalent lightweight pre-check, e.g. against `req.keys` size) to occur **before** `verify_state_proof`/`verify_membership` are invoked in `handle_get_requests`, so requests lacking sufficient bandwidth are rejected cheaply. Additionally, bound `GetRequestsWithProof.requests` and per-request `keys` to a fixed maximum size enforced early in `validate_unsigned`, and consider charging a minimal computational cost/deposit for unsigned GET-response submissions that fail the bandwidth check, so that both mempool validation and block execution short-circuit before the costly cryptographic work.

### Proof of Concept
1. Deploy an EVM app contract and dispatch a `DispatchGet` with `fee: 0` and a large `keys` array (self-relay, no bandwidth subscription purchased) — this succeeds and produces a valid pending `GetRequest` commitment, since neither `EvmHost.dispatch(DispatchGet)` [8](#0-7)  nor `pallet_ismp`'s dispatcher checks bandwidth allowance.
2. Off-chain, construct the corresponding `GetRequestsWithProof { requests, source, response, address }` with valid membership/state proofs for the batch of keys.
3. Submit this as `StateCoprocessor::handle_unsigned` repeatedly (or gossip it without ever including it in a block, relying only on `validate_unsigned`).
4. Each submission forces `handle_get_requests` to run `verify_membership` and, per request, `verify_state_proof` [9](#0-8)  for the full key set — before finally failing at `BandwidthGate::try_consume` due to no allowance on `(response.get.source, response.get.from)`.
5. Repeating this at scale (and across many peers via mempool gossip) consumes disproportionate node CPU/block-weight for free, with no fee paid and no bandwidth ever debited, matching the "excessive requests without financial penalties" bug class.

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

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-126)
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
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L375-396)
```rust
impl IsmpModule for ProxyModule {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Bandwidth gate. Always-enforce unless the `no-bandwidth` flag
		// is set; skipped for purchase messages so the recharge flow
		// itself doesn't need bandwidth. With the flag on the gate is a
		// no-op and this block is compiled out entirely.
		#[cfg(not(feature = "no-bandwidth"))]
		if !pallet_bandwidth::Pallet::<Runtime>::is_purchase_message(&request) {
			let bytes = ismp::abi::encode_post_request(&request).len() as u32;
			<pallet_bandwidth::Pallet<Runtime> as pallet_bandwidth::BandwidthGate>::try_consume(
				&request.source,
				&request.from,
				bytes,
			)
			.map_err(|err| {
				anyhow!(
					"bandwidth gate: {err} (source={:?}, from={:x?})",
					request.source,
					request.from
				)
			})?;
		}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L42-55)
```rust
/// Message for processing state queries
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, scale_info::TypeInfo,
)]
pub struct GetRequestsWithProof {
	/// The associated Get requests
	pub requests: Vec<GetRequest>,
	/// Proof of these requests on the source chain
	pub source: Proof,
	/// State proof of the requested values in the Get requests.
	pub response: Proof,
	/// Address that should be credited with fees
	pub address: Vec<u8>,
}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L111-152)
```rust
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
