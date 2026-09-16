Confirmed: `pallet-ismp-demo` is registered in the `gargantua` runtime's `IsmpModuleCallback` (`parachain/runtimes/gargantua/src/ismp.rs`, `parachain/runtimes/gargantua/src/lib.rs`), so it is not a test/mock-only pallet — it is production runtime code reachable by any relayer delivering a `PostRequest` from an EVM source chain.

### Title
Unvalidated UTF-8 in ISMP `PostRequest.body` causes undefined behavior via `String::from_utf8_unchecked` - (File: modules/pallets/demo/src/lib.rs)

### Summary
`IsmpModuleCallback::on_accept` in `pallet-ismp-demo`, which is wired into the Gargantua runtime's ISMP router, converts an attacker-controlled `PostRequest.body` byte vector into a `String` using `unsafe { String::from_utf8_unchecked(request.body) }` whenever the request's source state machine is `StateMachine::Evm(_)`, without any UTF-8 validation.

### Finding Description
```rust
// modules/pallets/demo/src/lib.rs:369-376
fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
	let source_chain = request.source;
	match source_chain {
		StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
			source: source_chain,
			data: unsafe { String::from_utf8_unchecked(request.body) },
		}),
		...
``` [1](#0-0) 

`request.body` originates from a relayed `PostRequest` delivered through `pallet-ismp`'s message-handling pipeline; any account able to dispatch a cross-chain `PostRequest` from an `Evm` source (an app on any connected EVM chain, since `body` is arbitrary calldata bytes with no schema) can set `body` to non-UTF-8 bytes. `from_utf8_unchecked` skips the validation that safe `String::from_utf8` performs, and the resulting `String` is then stored/emitted verbatim in a runtime event (`Event::Request { data, .. }`). This mirrors the Comrak AST issue precisely: a structure ([u8]/Vec<u8> field originating untrusted) is assumed to be valid UTF-8 and consumed via an unsafe/unchecked path without verifying that invariant, which is exactly CWE-755 "Improper Handling of Exceptional Conditions" from unvalidated data assumptions.

Because `String`'s safe API and much of the Rust standard library (including RPC JSON/SCALE serialization of events, `Display`/`Debug` formatting, and any downstream string slicing) rely on the invariant that `String` contents are valid UTF-8, holding an invalid `String` is undefined behavior. Depending on how the emitted event is later serialized (e.g., via the node's RPC layer for `system.events` subscriptions used by indexers/explorers), this can produce out-of-bounds reads, corrupted output, or panics when the byte sequence is subsequently sliced at a non-char boundary or otherwise treated as valid UTF-8 elsewhere in the runtime/RPC stack.

### Impact Explanation
This is a memory-safety/availability issue reachable by an unprivileged actor: any relayer/bridger delivering a `PostRequest` from an EVM chain to the pallet-ismp-demo module on Gargantua can construct a `body` that is invalid UTF-8, triggering UB in a live runtime that emits and stores this string in on-chain events. This is directly analogous to the referenced Comrak advisory's impact category (availability impact from unvalidated bytes treated as valid UTF-8) and falls within CWE-755 scope. Severity is bounded to the demo module's blast radius (event corruption / potential panic in downstream consumers of the "invalid" `String`), consistent with a Medium rating as in the original advisory.

### Likelihood Explanation
High likelihood of triggerability: producing non-UTF-8 bytes as a `PostRequest.body` from an EVM-side dApp requires no special privilege — it is ordinary calldata construction — and the ISMP dispatch/relay path (`pallet-ismp` handle → module router → `IsmpModuleCallback::on_accept`) is a standard, unprivileged message-delivery flow already exercised by relayers.

### Recommendation
Replace `unsafe { String::from_utf8_unchecked(request.body) }` with `String::from_utf8(request.body)` and handle the `Err` case (e.g., reject the request or emit a lossless byte representation such as hex) rather than assuming well-formed UTF-8 from an untrusted, attacker-supplied byte payload.

### Proof of Concept
1. From any EVM-connected chain, dispatch an ISMP `PostRequest` targeting the Gargantua parachain's `pallet-ismp-demo` module (`EXAMPLE_MODULE_ID`), with `body` set to an invalid UTF-8 byte sequence, e.g. `vec![0xff, 0xfe, 0x80]`.
2. Relay the request through the standard ISMP request-handling flow so it reaches `IsmpModuleCallback::on_accept`.
3. Because `source_chain` matches `StateMachine::Evm(_)`, the pallet executes `unsafe { String::from_utf8_unchecked(request.body) }` on the invalid bytes and stores it as `Event::Request.data`.
4. Any subsequent consumer treating this `String` as valid UTF-8 (RPC serialization, further string operations, or logging) invokes undefined behavior, matching the Comrak advisory's failure mode of assuming AST byte fields are valid UTF-8.

### Citations

**File:** modules/pallets/demo/src/lib.rs (L369-376)
```rust
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		let source_chain = request.source;

		match source_chain {
			StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
				source: source_chain,
				data: unsafe { String::from_utf8_unchecked(request.body) },
			}),
```
