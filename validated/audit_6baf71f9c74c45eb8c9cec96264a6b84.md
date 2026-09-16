## Title
Undefined behavior from `String::from_utf8_unchecked` on attacker-controlled cross-chain request body - ([File: modules/pallets/demo/src/lib.rs])

### Summary
`pallet-ismp-demo`, deployed live on the Gargantua runtime (`parachain/runtimes/gargantua/src/ismp.rs`, `parachain/runtimes/gargantua/src/lib.rs`), builds a `String` from an untrusted, attacker-supplied `PostRequest.body` using `String::from_utf8_unchecked` instead of the checked, validating `String::from_utf8`, whenever the message source is an EVM chain.

### Finding Description
`IsmpModuleCallback::on_accept` in `modules/pallets/demo/src/lib.rs` handles inbound ISMP `PostRequest`s. When the message's `source_chain` is `StateMachine::Evm(_)`, it does:

```rust
StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
    source: source_chain,
    data: unsafe { String::from_utf8_unchecked(request.body) },
}),
``` [1](#0-0) 

`request.body` is the raw byte payload of a `PostRequest` dispatched from any EVM-side sender through Hyperbridge's normal message-delivery pipeline (`Pallet::<T>::execute` → `handle_incoming_message` → router → `on_accept`), i.e. a completely attacker-controlled byte string. `String::from_utf8_unchecked` is documented as safe **only** if the caller guarantees the input is valid UTF-8; if it is not, the resulting `String` violates Rust's core memory-safety invariant (a `String` is guaranteed to be valid UTF-8), which is undefined behavior. UB in a `no_std` runtime context can manifest as unsound optimizations, heap corruption, or crashes depending on how the string is subsequently consumed (e.g., by wasm host functions, indexers, or SCALE-encoding this event for storage/RPC, all of which assume `String`'s UTF-8 invariant unconditionally).

This is a genuine root-cause defect distinct from the surrounding, correctly-guarded `Polkadot`/`Kusama` branch, which uses proper `codec::Decode` with error handling instead of an unchecked reinterpretation of raw bytes.

### Impact Explanation
Any single dispatched `PostRequest` from an EVM state machine with a non-UTF-8 body reaching `pallet-ismp-demo` on Gargantua triggers UB the moment the event is constructed/encoded. This can corrupt runtime memory or produce inconsistent state across nodes (since UB is not deterministic across compiler/optimization boundaries), which can manifest as a chain halt, panic, or divergent state — a route rendered unable to reliably deliver/process messages, and a memory-safety violation reachable by an unprivileged relayer/dispatcher with a single crafted message body. Because Gargantua is a live deployed runtime (`parachain/runtimes/gargantua/src/lib.rs`, `.../src/ismp.rs` wire the demo pallet in), this is not purely a test/mock-only path.

### Likelihood Explanation
High: the trigger condition is trivial — any non-UTF-8 byte sequence in the `body` field of an inbound EVM-sourced `PostRequest`, which is fully controlled by whoever dispatches from the EVM side (no signature, permission, or validation gates this field before it reaches the unsafe conversion).

### Recommendation
Replace `String::from_utf8_unchecked(request.body)` with `String::from_utf8(request.body)` and handle the `Err` case by rejecting the message (mirroring the pattern already used in the `Polkadot`/`Kusama` branch, which returns `IsmpError::Custom(...)` on decode failure) instead of invoking undefined behavior on malformed input.

### Proof of Concept
1. From any EVM-connected state machine, dispatch a `PostRequest` addressed to `pallet-ismp-demo`'s module id (`PALLET_ID = ModuleId::Pallet(PalletId(*b"ismp-ast"))`) with `body` set to an invalid UTF-8 byte sequence, e.g. `vec![0xFF, 0xFE, 0x80]`.
2. Once delivered and verified through the normal ISMP pipeline, `Pallet::<T>::execute` invokes `IsmpModuleCallback::on_accept` with this `PostRequest`.
3. Because `source_chain` is `StateMachine::Evm(_)`, the code executes `unsafe { String::from_utf8_unchecked(request.body) }` on the invalid bytes, producing a `String` that violates its UTF-8 invariant — undefined behavior, with observable consequences depending on how the resulting `Event::Request.data` is subsequently encoded/read (SCALE encoding of `String`, RPC serialization, or indexer consumption all assume valid UTF-8). [2](#0-1)

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
