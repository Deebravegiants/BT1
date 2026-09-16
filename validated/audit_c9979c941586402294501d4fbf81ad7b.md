Based on my research, the strongest candidate in-scope metering surface analogous to the CosmWasm "incorrect metering" bug class is `pallet-bandwidth`'s byte-based gate, which meters and enforces a prepaid allowance rather than a per-call gas/weight meter — but the underlying bug class (a metering primitive whose accounting doesn't match the real resource consumed, allowing under-charging) maps directly onto it.

### Title
Incorrect bandwidth metering allows undercharged/duplicated request delivery via forwarded and re-dispatched messages - (File: `parachain/runtimes/gargantua/src/ismp.rs`, `parachain/runtimes/nexus/src/ismp.rs`)

### Summary
`ProxyModule::on_accept` meters bandwidth once via `ismp::abi::encode_post_request(&request).len()` before deciding whether the request is destined for the local chain or must be forwarded onward, but the same request is fully re-processed (re-hashed, re-committed, and re-dispatched through `Ismp::dispatch_request`) on the forwarding path without any corresponding re-metering or fee attribution to the actual final consumer, meaning the "bytes" charged at ingress does not necessarily correspond to the true resource cost incurred as the message continues its journey.

### Finding Description
Every non-purchase POST request run through the gate is billed using a single, fixed formula: [1](#0-0) 

The gate call happens on `on_accept` — the entry point invoked once per `PostRequest` inside a batch — and if `request.dest != HostStateMachine::get()`, the request is not processed locally at all; instead it is forwarded via `Ismp::dispatch_request`, which re-commits the request to the offchain MMR for a new outbound delivery cycle: [2](#0-1) [3](#0-2) 

The metering is a flat `encode_post_request(&request).len()` charge applied identically regardless of whether the request terminates on this chain or is merely proxied onward for a second consensus-verified delivery leg to a further destination. Because `pallet-bandwidth`'s ledger is keyed by `(request.source, request.from)` — the *original* sender — and the bytes charged reflect only the wire-encoding of the single incoming leaf, a forwarded/proxied request consumes the exact same bandwidth as one that terminates locally, even though it imposes an additional consensus-verification and MMR-commitment cost on the destination side of the proxy hop. This is a metering/accounting mismatch between what is charged and what is actually consumed by the protocol, structurally analogous to the CosmWasm VM's "incorrect metering" class, where the meter used to bound/charge for execution didn't correctly track the real work performed.

Separately, `pallet-messaging-incentives::message_bytes` and the `WeightFeeHandler` in `modules/pallets/ismp/src/fee_handler.rs` independently derive their own byte/weight figures from the same messages using different formulas (`max(body.len(), 32)` summed per-request vs. `encode_post_request` full envelope length), so the three metering surfaces (bandwidth gate, relayer reputation mint, and transaction fee) can diverge for the same message, and none of them account for the multi-hop/proxy forwarding cost described above: [4](#0-3) [5](#0-4) 

### Impact Explanation
An app that is allowed to act as (or is unwittingly used as) a proxy chain can send POST requests destined for a further downstream chain and be billed only the single-hop `pallet-bandwidth` cost while causing Hyperbridge to perform a second full dispatch/commitment cycle (MMR insertion, event emission, eventual relayer delivery) for the forwarded leg. Because the byte-allowance economic model was explicitly built to replace "protocol fee on every dispatch" for the *dispatching* app, but forwarding is not separately billed, an attacker (or normal usage pattern) can amplify the actual bytes moved through the protocol relative to what was purchased, degrading the bandwidth model's guarantee that "the cost was paid at purchase time" and creating a resource/cost mismatch for chain operators who fund relaying of the second hop. This is a Medium-severity economic/metering-correctness issue rather than a direct fund-theft bug.

### Likelihood Explanation
Reaching this path requires only a permissionless, unprivileged POST dispatch from any registered source chain whose `request.dest` is set to a third state machine rather than the Hyperbridge/local one, and requires the host to be configured as an allowed proxy (`host.is_allowed_proxy`) for that source — a supported, intentional feature (`request/handle.rs` lines 75-83), not a misconfiguration. No privileged role, admin action, or governance manipulation is required by the party dispatching the message; only the standard trust configuration that proxying is expected to support.

### Recommendation
Re-meter (or additionally meter) bandwidth at the point of re-dispatch on the proxy hop (`Ismp::dispatch_request` call in `on_accept`) rather than relying solely on the ingress charge, or explicitly document/enforce that the bandwidth allowance model is not compatible with proxied/multi-hop destinations and reject forwarding for gated apps. Additionally, reconcile the three independent byte-counting formulas (`encode_post_request` in the bandwidth gate, `max(body.len(),32)` in messaging-incentives, and whatever `MessageResult::weight()` reports to `WeightFeeHandler`) so metering used for economic enforcement is derived from one canonical, audited source of truth.

### Proof of Concept
1. Register `pallet-bandwidth::set_manager` and purchase a tier for `(source_chain, app)` on Hyperbridge.
2. Configure Hyperbridge (`host.is_allowed_proxy`) to treat `source_chain` as an allowed proxy for a further downstream `dest_chain` that has no direct consensus client registered on Hyperbridge (satisfying `check_state_machine_client`).
3. From `app`, dispatch a POST request with `dest = dest_chain` (not Hyperbridge's own `HostStateMachine`).
4. Observe in `ProxyModule::on_accept` that `pallet_bandwidth::try_consume` is charged once for `encode_post_request(&request).len()` bytes, then the request is forwarded via `Ismp::dispatch_request`, causing a fresh commitment/MMR insertion and a second full relayer-delivery cycle to `dest_chain` — consuming twice the protocol resources (proof verification + MMR + relaying) for the price of a single-hop charge. [6](#0-5)

### Citations

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

**File:** parachain/runtimes/gargantua/src/ismp.rs (L398-404)
```rust
		if request.dest != HostStateMachine::get() {
			Ismp::dispatch_request(
				Request::Post(request),
				FeeMetadata::<Runtime> { payer: [0u8; 32].into(), fee: Default::default() },
			)?;
			return Ok(Weight::from_parts(0, 0));
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

**File:** modules/pallets/messaging-incentives/src/lib.rs (L126-135)
```rust
	fn message_bytes(message: &Message) -> u32 {
		match message {
			Message::Request(req) => req
				.requests
				.iter()
				.map(|p| core::cmp::max(p.body.len() as u32, 32))
				.sum::<u32>(),
			_ => 0,
		}
	}
```

**File:** modules/pallets/ismp/src/fee_handler.rs (L168-181)
```rust
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		_events: Vec<Event>,
	) -> DispatchResultWithPostInfo {
		if !POLICY {
			return Ok(PostDispatchInfo { actual_weight: None, pays_fee: Pays::No })
		}
		let mut total_weight = Weight::zero();
		let treasury_account: AccountId = T::get().into_account_truncating();

		for message in &messages {
			let weight = message.weight;
			total_weight.saturating_accrue(weight);
			let fee = W::weight_to_fee(&weight);
```

**File:** modules/ismp/core/src/handlers/request.rs (L75-84)
```rust
		// in order to allow proxies, the host must configure the given state machine
		// as it's proxy and must not have a state machine client for the source chain
		let allow_proxy = host.is_allowed_proxy(&msg.proof.height.id.state_id) &&
			check_state_machine_client(source_chain);

		// check if the request is allowed to be proxied
		if source_chain != msg.proof.height.id.state_id && !allow_proxy {
			Err(Error::RequestProxyProhibited { meta: req.clone().into() })?
		}
	}
```
