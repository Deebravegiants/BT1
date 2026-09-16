### Title
Unchecked UTF-8 conversion of untrusted cross-chain message body causes undefined behavior - ([File: modules/pallets/demo/src/lib.rs])

### Summary
The external report describes a class of bug where cross-chain-synced data is deserialized/consumed without runtime validation of its structure, so malformed or malicious input silently propagates into application state. The closest reachable analog in Hyperbridge is `IsmpModuleCallback::on_accept` in `modules/pallets/demo/src/lib.rs`, which converts an attacker-controlled `PostRequest.body` to a `String` using `String::from_utf8_unchecked` without verifying the bytes are valid UTF-8, unlike the JSON.parse-without-schema-check pattern in the original report.

### Finding Description
`on_accept` handles inbound ISMP POST requests dispatched from any EVM-connected chain. For `StateMachine::Evm(_)` sources, the module does: [1](#0-0) 
`request.body` is fully attacker-controlled — any unprivileged dispatcher on the source EVM chain can set the `DispatchPost.body` to arbitrary bytes when sending a POST request to this module. `String::from_utf8_unchecked` is documented by Rust as **undefined behavior** if the input is not valid UTF-8; unlike `JSON.parse` (which at least performs syntax validation), this API performs **no runtime validation whatsoever** of the byte content before it is treated as a UTF-8 string. This exactly mirrors the reported bug class: a type coercion (`as StoredGrantedPermission` in the original; `unsafe` UTF-8 assumption here) is being used as a stand-in for real schema/format verification of untrusted, cross-chain-synced data.

### Impact Explanation
`from_utf8_unchecked` on non-UTF-8 input is undefined behavior in Rust — depending on compiler optimizations this can produce corrupted string data that is then stored on-chain via `Event::Request { data, .. }` (deposited into runtime storage/events), or in the worst case cause miscompilation-driven memory-safety issues. Because this runs inside `on_accept`, which is invoked automatically whenever a relayer submits a valid consensus/state proof for an inbound POST request (no permission check on the request body's content), a single crafted message from an unprivileged sender that is otherwise properly proven can trigger this undefined behavior across all collators that execute the block, risking a state-transition mismatch/chain halt.

### Likelihood Explanation
Reaching this code path only requires: (1) dispatching a POST request from an EVM chain destined to this pallet's module id, and (2) a relayer delivering it with a valid HandlerV2/consensus proof — both standard, permissionless operations available to any relayer or user willing to pay dispatch/relay fees. No governance, admin, or privileged role is needed. The attacker fully controls the `body` bytes and can trivially supply invalid UTF-8 (e.g. a lone continuation byte `0x80`).

### Recommendation
Replace `String::from_utf8_unchecked(request.body)` with `String::from_utf8(request.body)` and reject (or lossily convert via `String::from_utf8_lossy`) messages whose body is not valid UTF-8, returning an `IsmpError` instead of invoking undefined behavior. More generally, apply explicit schema/format validation (bounds, encoding, structure) to every field decoded out of a `PostRequest.body`, `GetResponse` value, or other cross-chain payload before it is used or persisted, consistent with the fix pattern (zod-style validation) described in the referenced report.

### Proof of Concept
1. On an EVM chain, call `IDispatcher(host).dispatch(DispatchPost({ dest: <this-parachain>, to: <demo-pallet-module-id>, body: hex"80", timeout: 0, fee: 0, payer: msg.sender }))` — `0x80` is a byte that is invalid as the start of any UTF-8 sequence.
2. Relayer submits the request with proof through `handle_unsigned`/`HandlerV2`, which is delivered to `pallet-ismp`, invoking `IsmpModuleCallback::on_accept` on the demo pallet.
3. `unsafe { String::from_utf8_unchecked(request.body) }` executes on the invalid byte sequence, producing UB (an invalid/corrupted `String` used in `Event::Request`), rather than an error. [2](#0-1)

### Citations

**File:** modules/pallets/demo/src/lib.rs (L368-399)
```rust
impl<T: Config> IsmpModule for IsmpModuleCallback<T> {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		let source_chain = request.source;

		match source_chain {
			StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
				source: source_chain,
				data: unsafe { String::from_utf8_unchecked(request.body) },
			}),
			StateMachine::Polkadot(_) | StateMachine::Kusama(_) => {
				let payload =
					<Payload<T::AccountId, <T as Config>::Balance> as codec::Decode>::decode(
						&mut &*request.body,
					)
					.map_err(|_| IsmpError::Custom("Failed to decode request data".to_string()))?;
				<T::NativeCurrency as Mutate<T::AccountId>>::mint_into(
					&payload.to,
					payload.amount.into(),
				)
				.map_err(|_| IsmpError::Custom("Failed to mint funds".to_string()))?;
				Pallet::<T>::deposit_event(Event::<T>::BalanceReceived {
					from: payload.from,
					to: payload.to,
					amount: payload.amount,
					source_chain,
				});
			},
			source => Err(IsmpError::Custom(format!("Unsupported source {source:?}")))?,
		}

		Ok(weight())
	}
```
