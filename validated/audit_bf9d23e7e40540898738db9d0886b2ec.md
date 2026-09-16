### Title
Undefined Behavior via Unchecked UTF-8 Conversion of Attacker-Controlled Request Body - ([File: modules/pallets/demo/src/lib.rs])

### Summary
The `ismp-demo` pallet's `on_accept` callback, which is compiled into the Gargantua parachain runtime and reachable by any relayer submitting an unsigned `pallet_ismp::Call::handle_unsigned` extrinsic carrying a `PostRequest` from an EVM source chain, converts the fully attacker-controlled request body into a `String` using `String::from_utf8_unchecked`, bypassing UTF-8 validation entirely.

### Finding Description
In `IsmpModuleCallback::on_accept`, when the source state machine is `StateMachine::Evm(_)`, the pallet does: [1](#0-0) 

```rust
match source_chain {
    StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
        source: source_chain,
        data: unsafe { String::from_utf8_unchecked(request.body) },
    }),
```

`request.body` is arbitrary bytes chosen by whoever dispatches the POST request from an EVM state machine and delivered by any relayer through `pallet_ismp::Pallet::<T>::execute` / `handle_unsigned`, which the ISMP handler module resolves to this callback's `on_accept`. `String::from_utf8_unchecked` is documented by Rust as requiring the caller to *guarantee* the input is valid UTF-8; violating this invariant is undefined behavior, because every other `std`/`alloc` API that operates on `String`/`&str` (character iteration, byte-boundary slicing, `Display`, FFI boundary crossings, indexers used by the event-emission/encoding machinery) assumes the UTF-8 invariant holds and will perform unchecked memory reads based on it. This is the direct structural analog of CVE-2024-29645: an attacker-supplied, insufficiently validated buffer is consumed by a routine that skips the bounds/format check normally required before further processing, letting downstream consumers read or interpret memory outside the intended structure.

Because this event data is subsequently encoded/emitted on-chain and can be consumed by off-chain indexers or on-chain logic that assumes well-formed UTF-8, an adversary who crafts a message body with invalid UTF-8 byte sequences (e.g., a lone continuation byte, an overlong encoding, or a truncated multi-byte sequence at the end of the buffer) can trigger unsound behavior anywhere the resulting `String` is subsequently sliced or iterated by index — turning an ordinary POST request into a vector for out-of-bounds memory access.

### Impact Explanation
`String`/`&str` in Rust rely on the UTF-8 invariant for memory safety in many standard operations (byte-boundary slicing, `char_indices`, `Chars`, etc.). Once that invariant is broken via `from_utf8_unchecked` on untrusted data, any later code path that treats the value as a valid `&str` and slices it at a byte offset (a very common pattern for string processing/formatting/truncation in Substrate event codecs, RPC serializers, or downstream consumers) can compute buffer bounds under a false assumption, leading to out-of-bounds reads/panics or, in principle, unsound memory access consistent with a High severity buffer-overflow-class bug in a component processing untrusted, attacker-supplied data.

### Likelihood Explanation
Any unprivileged relayer can trigger `on_accept` for this module by delivering a `PostRequest` targeted at the `ismp-demo` pallet's module ID from an EVM-sourced state machine, with the request body fully attacker-controlled. This flows through the standard `pallet_ismp::Call::handle_unsigned` extrinsic path (in-scope per the task rules) and requires no special privileges — just a valid ISMP delivery proof for the request, which any relayer can construct for messages destined to this pallet.

### Recommendation
Replace `String::from_utf8_unchecked(request.body)` with `String::from_utf8(request.body)` and handle the `Err` case (e.g., reject the request or store the raw bytes / lossy-decoded string) instead of asserting an invariant that untrusted, attacker-controlled bytes cannot be guaranteed to satisfy.

### Proof of Concept
1. On the EVM source chain, dispatch (or have any account dispatch) a POST request destined for the `ismp-demo` module on the Gargantua parachain with `body` set to a byte sequence that is not valid UTF-8, e.g. `[0xC1, 0x81]` (an overlong encoding) or `[0xE6, 0x97]` (a truncated 3-byte sequence).
2. Any relayer submits the corresponding proof via `pallet_ismp::Call::handle_unsigned`.
3. `IsmpModuleCallback::on_accept` is invoked with `source_chain = StateMachine::Evm(_)`, executing `unsafe { String::from_utf8_unchecked(request.body) }` on the invalid bytes, producing a `String` that violates Rust's UTF-8 invariant.
4. Any subsequent code that treats this `Event::Request.data` field as a valid `&str` (e.g., truncation, `char_indices`, FFI, or off-chain indexer libraries built on the assumption of valid UTF-8) can then read out of the intended byte boundaries. [2](#0-1)

### Citations

**File:** modules/pallets/demo/src/lib.rs (L368-396)
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
```
