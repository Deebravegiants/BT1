### Title
Unchecked `String::from_utf8_unchecked` on attacker-controlled ISMP request body causes undefined behavior - (File: `modules/pallets/demo/src/lib.rs`)

### Summary
`IsmpModuleCallback::on_accept` in the `ismp-demo` pallet builds a `String` from an inbound EVM `PostRequest.body` using the unsafe, unchecked UTF-8 constructor. This mirrors the CVE-2024-23310 bug class: attacker-supplied bytes are consumed by an unsafe/unchecked parsing routine that assumes a well-formed input invariant, producing memory-unsafe state when that invariant is violated.

### Finding Description
`on_accept` is the `IsmpModule` callback invoked by `pallet-ismp`'s dispatcher whenever an inbound `PostRequest` destined for this module is delivered and successfully proof-verified. For a source of `StateMachine::Evm(_)`, the handler does: [1](#0-0) 

`request.body` is fully attacker-controlled: it is the raw bytes carried by a cross-chain `PostRequest` originating from any connected EVM state machine, delivered by any unprivileged relayer submitting a valid state/consensus proof for that message. `String::from_utf8_unchecked` skips UTF-8 validation entirely — its safety contract requires the caller to guarantee the bytes are valid UTF-8. Because the input is attacker-controlled and unchecked, an adversary can trivially construct a `PostRequest.body` containing arbitrary invalid UTF-8 byte sequences.

The resulting `String` violates the core invariant the Rust standard library relies on for all `str`/`String` safety guarantees (`std::str` APIs assume valid UTF-8 to justify skipping bounds/validity checks when slicing, iterating chars, doing byte-boundary arithmetic, or when downstream code/log formatting reasons about char boundaries). This is directly analogous to the CVE's root cause: an unchecked parse of attacker-supplied bytes that violates an internal representation invariant, producing undefined behavior reachable from a single malicious file/message. Here the "malicious file" is the relayed ISMP message body.

### Impact Explanation
Once the invariant is broken, any subsequent operation that depends on the `String`'s UTF-8 validity (slicing at byte offsets, `Display`/logging, serialization, further string processing in the runtime or off-chain tooling that consumes this event data) is undefined behavior in Rust — this can manifest as out-of-bounds reads, panics, or corrupted memory reads within the process (parachain collator/validator node), not merely an application-level logic error. Because `deposit_event` stores the value in on-chain event storage, the malformed value can also propagate to indexers/relayers/tesseract processes that decode and act on event data, spreading the unsafety to downstream consumers.

### Likelihood Explanation
Reachability requires only a single relayed `PostRequest` from an EVM state machine targeting the `ismp-demo` module — no privileged role, governance, or special conditions are needed; any relayer can construct and deliver such a message given a valid proof for an already-finalized EVM block. The pallet is wired into the `gargantua` runtime's ISMP router, so if `gargantua` is a deployed/production runtime, this is reachable in production.

### Recommendation
Replace `String::from_utf8_unchecked(request.body)` with `String::from_utf8(request.body)` and handle the `Err` case (e.g., reject the request or emit a lossy/hex-encoded event), removing the `unsafe` block entirely. There is no performance justification for skipping validation here since the body size is bounded by ISMP message size limits and this runs once per accepted request.

### Proof of Concept
1. On the EVM side, submit any application dispatch that produces a `PostRequest` with `body` set to an invalid UTF-8 byte sequence (e.g., a single `0xFF` byte, or a truncated multi-byte sequence like `0xE2 0x82`), destined for the `ismp-demo` module (`to = PALLET_ID.to_bytes()`), targeting a `Polkadot`/`Kusama` parachain running this pallet (this only needs `source_chain` to be `StateMachine::Evm(_)` — routing is otherwise identical to the legitimate transfer path).
2. Relay the message with a valid consensus/state proof through the normal ISMP `handle_unsigned` request-delivery path; no signer or governance permission is required beyond being able to submit a well-formed proof for the message.
3. `pallet-ismp` decodes/verifies the message and dispatches to `IsmpModuleCallback::on_accept`, which executes `unsafe { String::from_utf8_unchecked(request.body) }` on the malicious bytes, constructing a `String` that does not contain valid UTF-8 — violating the safety invariant relied upon by the Rust standard library and any downstream consumer of the `Event::Request { data, .. }` event. [1](#0-0)

### Citations

**File:** modules/pallets/demo/src/lib.rs (L368-377)
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
```
