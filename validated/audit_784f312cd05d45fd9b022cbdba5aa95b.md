### Title
Single unregistered destination module (`to`) in a batched `handle_unsigned` call causes the entire batch of otherwise-valid, proof-verified requests to be rejected - (File: `modules/pallets/ismp/src/impls.rs`)

### Summary
`Pallet::execute` in pallet-ismp collects the per-request outcomes of an entire `handle_unsigned` batch into a single `Result<Vec<Event>, Error>` via `.collect()`. Because Rust's `collect::<Result<Vec<_>,_>>()` short-circuits on the first `Err`, one request in the batch that targets a destination module id the router does not recognize is enough to fail the whole extrinsic with `Error::InvalidMessage`, discarding every other legitimately proven request bundled in the same call.

### Finding Description
`handle::<H>` in `modules/ismp/core/src/handlers/request.rs` processes each request in a `RequestMessage` independently, storing each request's outcome as a `Result<Event, Error>` in a `Vec`: [1](#0-0) 

The router lookup `router.module_for_id(request.to.clone())?` inside that per-request closure fails whenever `request.to` does not match a configured module id, exactly as documented for `IsmpRouter`: [2](#0-1) 

and as implemented by production runtime routers, which explicitly return `Err(anyhow!("Destination module not found"))` for any unrecognized `to`: [3](#0-2) [4](#0-3) 

`request.to` is attacker/source-chain controlled — any application dispatching a `PostRequest` (e.g. via `EvmHost.dispatch`) picks an arbitrary destination module/address with no existence check on the source chain: [5](#0-4) 

When a relayer batches multiple pending messages into a single `handle_unsigned` call (the pallet's normal, unsigned, permissionless entrypoint), `Pallet::execute` flattens every request's `Result<Event,Error>` across the whole batch and then does a single fallible `collect`: [6](#0-5) 

Because this `.collect::<Result<Vec<_>, _>>()` is all-or-nothing, a single `ModuleNotFound`/"Destination module not found" error anywhere in the flattened set aborts the extrinsic with `Error::<T>::InvalidMessage` and Substrate's transactional dispatch rolls back the entire call — including the successfully verified and receipted requests for unrelated, legitimate destination modules that happened to be batched in the same transaction.

### Impact Explanation
This is a route-availability failure directly matching the CVE's bug class (a single non-existent target derails processing of the whole batch/pipeline). Any unprivileged sender on a source chain can dispatch one POST request with a garbage/non-existent `to` module id. If a relayer (or the attacker themselves, since `handle_unsigned` is permissionless and unsigned) bundles that request together with other pending, legitimate requests into one `handle_unsigned` call, delivery of every request in that batch fails, even though their proofs were valid and independently verifiable. This is a denial-of-service on message delivery — "a route unable to deliver messages" — reachable from a single submitted request with no privileged access required.

### Likelihood Explanation
High reachability: any application/contract that can dispatch an ISMP POST request controls the `to` field and can target a nonexistent module id trivially. Relayers commonly batch multiple pending requests per delivery transaction for gas/proof efficiency, so the poisoned request need only be observed pending alongside legitimate ones to be swept into the same `handle_unsigned` call, at which point the failure is automatic and requires no further attacker action.

### Recommendation
Change `Pallet::execute` to process each request's outcome independently instead of short-circuiting the whole batch: collect successes and failures separately (e.g. `Vec<Result<Event, Error>>` without the fallible `collect`), emit `Error` events only for the failing requests, and still deposit/finalize events and charge fees for the requests that succeeded, mirroring the per-request isolation already implemented in `handlers::request::handle`.

### Proof of Concept
1. Attacker (or any dApp) dispatches `PostRequest` A on chain X with `to = <valid, existing module id>` and `PostRequest` B on chain X with `to = <garbage id, no router match>`, both destined for chain Y.
2. A relayer observes both pending requests, builds proofs for both, and submits a single `handle_unsigned { messages: [Message::Request(RequestMessage{requests: [A, B], ...})] }` extrinsic on chain Y (or bundles them across separate messages in the same call).
3. `handlers::request::handle` verifies the shared membership proof for both A and B (succeeds), then dispatches to modules: A succeeds via `on_accept`, B fails with `Error::ModuleNotFound`/"Destination module not found" from `router.module_for_id`.
4. `Pallet::execute`'s flatten+`collect::<Result<Vec<_>,_>>()` over both requests' results encounters B's `Err` and returns `Err(Error::InvalidMessage)` for the whole extrinsic; the entire transaction reverts, so request A — despite being fully valid and proven — is never delivered/receipted in this call and must be retried in a future batch, giving the attacker a mechanism to degrade delivery of any request they can get bundled alongside their garbage-`to` request.

### Citations

**File:** modules/ismp/core/src/handlers/request.rs (L96-134)
```rust
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};

			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

	Ok(MessageResult::Request { events: result, weight: total_weights })
```

**File:** docs/content/protocol/ismp/router.mdx (L10-16)
```text
```rust showLineNumbers
pub trait IsmpRouter {
    /// Should decode the module id and return a handler to the appropriate `IsmpModule`
    /// implementation
    fn module_for_id(&self, bytes: Vec<u8>) -> Result<Box<dyn IsmpModule>, anyhow::Error>;
}
```
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L406-421)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_accept(request),

			#[cfg(not(feature = "no-bandwidth"))]
			id if id == ModuleId::Pallet(pallet_bandwidth::pallet::PALLET_BANDWIDTH) =>
				pallet_bandwidth::Pallet::<Runtime>::default().on_accept(request),

			pallet_hyper_fungible_token::PALLET_ID =>
				pallet_hyper_fungible_token::Pallet::<Runtime>::default().on_accept(request),

			_ => Err(anyhow!("Destination module not found")),
		}
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L401-410)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			id if id == ModuleId::Pallet(pallet_bandwidth::pallet::PALLET_BANDWIDTH) =>
				pallet_bandwidth::Pallet::<Runtime>::default().on_accept(request),
			pallet_hyper_fungible_token::PALLET_ID =>
				pallet_hyper_fungible_token::Pallet::<Runtime>::default().on_accept(request),
			_ => Err(anyhow!("Destination module not found")),
		}
```

**File:** evm/src/core/EvmHost.sol (L921-930)
```text
    function dispatch(DispatchPost memory post) external payable notFrozen returns (bytes32 commitment) {
        if (msg.value > 0) {
            address[] memory path = new address[](2);
            address uniswapV2 = _hostParams.uniswapV2;
            path[0] = IUniswapV2Router02(uniswapV2).WETH();
            path[1] = feeToken();
            IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msg.value}(
                post.fee, path, address(this), block.timestamp
            );
        } else if (post.fee > 0) {
```

**File:** modules/pallets/ismp/src/impls.rs (L59-76)
```rust
		let events = message_results
			.into_iter()
			// check that requests will be successfully dispatched
			// so we can not be spammed with failing txs
			.map(|result| match result {
				MessageResult::Request { events, .. } |
				MessageResult::Response { events, .. } |
				MessageResult::Timeout { events, .. } => events,
				MessageResult::ConsensusMessage(events) => events.into_iter().map(Ok).collect(),
				MessageResult::FrozenClient(_) => vec![],
			})
			.flatten()
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;
```
