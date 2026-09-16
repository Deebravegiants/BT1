### Title
Non-atomic `handle_unsigned` in `pallet-state-coprocessor` permanently consumes app bandwidth allowance on batch failure - (File: `modules/pallets/state-coprocessor/src/lib.rs`)

### Summary
`pallet_state_coprocessor::Pallet::handle_unsigned` is an unauthenticated, unsigned extrinsic (`ensure_none(origin)`) that anyone can submit for free. Unlike `pallet_ismp::handle_unsigned`, which is explicitly annotated `#[frame_support::transactional]` so any mid-batch failure reverts all storage effects, the coprocessor's `handle_unsigned` has no such annotation. Its body, `Self::handle_get_requests`, performs real, persistent storage mutations (bandwidth-allowance consumption, reputation minting, MMR insertion, receipt/commitment writes) *before* the batch is fully validated, and only returns an error at the end if a later item in the batch fails. Because the call isn't transactional, those earlier mutations are permanently committed even though the extrinsic reports `Error::HandlingError` and the caller sees a failed batch.

### Finding Description
`handle_unsigned` in `modules/pallets/state-coprocessor/src/lib.rs`: [1](#0-0) 
calls `Self::handle_get_requests` with no `#[frame_support::transactional]` wrapper, in contrast to `pallet_ismp::handle_unsigned`, which is explicitly wrapped: [2](#0-1) 

`handle_get_requests` (in `modules/pallets/state-coprocessor/src/impls.rs`) processes a `Vec<GetRequest>` batch in two sequential per-item loops that each perform persistent storage writes:

1. The proof-verification loop calls `BandwidthGate::try_consume` for every request in the batch, which mutates `pallet_bandwidth::Allowance` storage (draining an app's prepaid byte allowance) and deposits an event, per request, before the whole batch is known to succeed: [3](#0-2) 
`try_consume` itself performs an unconditional `StorageDoubleMap::mutate` that drains the FIFO subscription list: [4](#0-3) 

2. The delivery loop then stores response receipts and dispatches each `GetResponse`, which (via `dispatch_get_response`) pushes an MMR leaf and writes `ResponseCommitments`/`Responded` storage and events: [5](#0-4) 

Since a `Vec<GetRequest>` batch is processed item-by-item and only the last item's failure (e.g., insufficient state proof, duplicate response, or a later item exceeding the app's remaining bandwidth allowance) causes `handle_get_requests` to return `Err(...)`, all writes performed for earlier items in the same batch — most importantly the bandwidth-allowance drain in step 1 — are **not rolled back**. The overall extrinsic then bubbles up `Error::<T>::HandlingError` to the caller: [6](#0-5) 

This is the same bug class as OpenBao's Kerberos issue: an unauthenticated path performs real, resource-consuming side effects while ultimately surfacing only an error, hiding the fact that state was mutated.

### Impact Explanation
Any unprivileged relayer can submit a crafted `handle_unsigned` batch to `pallet-state-coprocessor` containing multiple `GetRequest`s targeting a victim app's `(source, from)` bandwidth allowance. By ordering the batch so that early items pass proof verification and consume bandwidth via `BandwidthGate::try_consume`, while a later item is deliberately malformed (bad state proof, duplicate response, or one that itself exceeds the remaining allowance), the attacker forces the whole extrinsic to fail with `Error::HandlingError` — yet the bandwidth already drained for the earlier items in `pallet_bandwidth::Allowance` is permanently committed, and no legitimate `GetResponse` was ever delivered for that consumed allowance. Repeating this — at zero cost, since the extrinsic is unsigned — permanently exhausts a target app's prepaid bandwidth quota (a purchased, real resource) without ever delivering the responses it paid for, denying the app the ability to have its legitimate `GetRequest`s answered (availability impact), matching the CVSS `A:L` component of the analog advisory.

### Likelihood Explanation
High: the entry point is fully unauthenticated (`ensure_none`), requires no fee or stake (unsigned extrinsic), and the attacker fully controls the crafted `Message::Response`/`GetRequestsWithProof` batch content and ordering. No special privileges, governance, or off-chain infrastructure compromise are needed — only knowledge of a valid source-chain proof for the first request(s) (obtainable from any relayer since it's the same proof format used by honest relayers) and a request designed to fail near the end of the batch.

### Recommendation
Wrap `pallet_state_coprocessor::Pallet::handle_unsigned` (and any other entry point invoking `handle_get_requests`) with `#[frame_support::transactional]`, mirroring `pallet_ismp::handle_unsigned`, so that a failure anywhere in batch processing reverts all storage effects from that call, including bandwidth-allowance consumption, MMR insertion, and receipt/commitment writes.

### Proof of Concept
1. Attacker acquires (or fabricates, if a subscription with nonzero remaining bytes already exists for the victim `(source, app)` key) valid source/response proofs for two `GetRequest`s addressed to a victim app that has a bandwidth subscription with `N` remaining bytes.
2. Attacker submits an unsigned `state-coprocessor.handle_unsigned(GetRequestsWithProof { requests: [req1, req2], source, response, address })` where `req1`'s response fits comfortably under `N` bytes, and `req2` is crafted to fail later in `handle_get_requests` (e.g., a `DuplicateResponse` via a pre-seeded `response_receipt`, or by making `req2`'s size exceed the now-reduced remaining allowance so `try_consume` errors).
3. `handle_get_requests` iterates the batch: `req1` passes `verify_state_proof` and calls `BandwidthGate::try_consume`, mutating `pallet_bandwidth::Allowance` to drain `req1`'s bytes — this write commits directly to storage.
4. Processing `req2` fails (`Err(...)`) and `handle_get_requests` returns `Err`; `handle_unsigned` maps this to `Error::<T>::HandlingError` and the extrinsic fails.
5. Because `handle_unsigned` is not `#[transactional]`, the `Allowance` mutation from step 3 persists on-chain despite the extrinsic's failure. Repeat to exhaust the victim's entire allowance for free while never delivering the paid-for `GetResponse`s.

### Citations

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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L133-155)
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

			responses.push(response);
		}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L188-237)
```rust
		for get_response in responses {
			host.store_response_receipt(&get_response, &address)?;
			Self::dispatch_get_response(get_response, address.clone())
				.map_err(|_| Error::Custom("Failed to dispatch get response".to_string()))?;
		}

		Ok(())
	}

	/// Insert a get response into the MMR and emits an event
	pub fn dispatch_get_response(
		get_response: GetResponse,
		address: Vec<u8>,
	) -> Result<(), ismp::Error> {
		let commitment = hash_get_response::<<T as Config>::IsmpHost>(&get_response);
		let req_commitment =
			hash_request::<<T as Config>::IsmpHost>(&Request::Get(get_response.get.clone()));
		let event = pallet_ismp::Event::Response {
			request_nonce: get_response.get.nonce,
			dest_chain: get_response.get.source,
			source_chain: get_response.get.dest,
			commitment,
			req_commitment,
		};

		let leaf_index_and_pos = <T as Config>::Mmr::push(Leaf::GetResponse(get_response));
		let meta = FeeMetadata::<T> { payer: [0u8; 32].into(), fee: Default::default() };

		pallet_ismp::child_trie::ResponseCommitments::<T>::insert(
			commitment,
			RequestMetadata {
				offchain: LeafIndexAndPos {
					leaf_index: leaf_index_and_pos.index,
					pos: leaf_index_and_pos.position,
				},
				fee: meta,
				claimed: true,
			},
		);
		pallet_ismp::Responded::<T>::insert(req_commitment, true);
		pallet_ismp::Pallet::<T>::deposit_event(event.into());
		let event = pallet_ismp::Event::GetRequestHandled(RequestResponseHandled {
			commitment: req_commitment,
			relayer: address.clone(),
		});

		pallet_ismp::Pallet::<T>::deposit_event(event.into());

		Ok(())
	}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L509-564)
```rust
impl<T: Config> BandwidthGate for Pallet<T> {
	fn try_consume(
		source: &ismp::host::StateMachine,
		app: &[u8],
		bytes: u32,
	) -> Result<(), GateError> {
		let key = AppKey::truncate_from(app.to_vec());
		if Allowlist::<T>::contains_key(source, &key) {
			return Ok(());
		}

		let need: u128 = bytes.into();
		let now = <T as pallet_ismp::Config>::TimestampProvider::now().as_secs();

		let total = pallet::Allowance::<T>::mutate(source, &key, |list| {
			// Sweep expired in-place. Order-preserving.
			list.retain(|s| s.expires_at > now);

			if list.is_empty() {
				return Err(GateError::NoAllowance);
			}

			let total: u128 = list.iter().map(|s| s.remaining_bytes).sum();
			if total < need {
				return Err(GateError::Insufficient { remaining: total, required: need });
			}

			// Drain from the front in insertion order. Once a sub is
			// fully consumed, pop it and continue with the next.
			// `get_mut` defends against a malformed list that satisfies
			// the `total >= need` precheck but is structurally empty;
			// we'd otherwise panic via `list[0]`.
			let mut left = need;
			while left > 0 {
				let Some(head) = list.get_mut(0) else {
					return Err(GateError::NoAllowance);
				};
				let take = head.remaining_bytes.min(left);
				head.remaining_bytes = head.remaining_bytes.saturating_sub(take);
				left = left.saturating_sub(take);
				if head.remaining_bytes == 0 {
					list.remove(0);
				}
			}

			Ok(total)
		})?;

		Self::deposit_event(Event::BandwidthConsumed {
			source: *source,
			app: key,
			bytes: need,
			remaining: total - need,
		});
		Ok(())
	}
```
