### Title
Unchecked UTF-8 Assumption on Attacker-Controlled ISMP Request Body Causes Undefined Behavior via `String::from_utf8_unchecked` - ([File: modules/pallets/demo/src/lib.rs])

### Summary
`pallet_ismp_demo::IsmpModuleCallback::on_accept` builds a `String` directly from an incoming EVM `PostRequest.body` using `unsafe { String::from_utf8_unchecked(request.body) }`, with no prior validation that the bytes are well-formed UTF-8. This is the same bug class as the reported uutils `sort` issue — code that "enforces UTF-8 encoding" implicitly but never actually checks it — except here the unchecked path is `unsafe`, so a malformed input does not merely panic, it produces a `String` whose safety invariant is violated (Rust's `String` type guarantees valid UTF-8 to the compiler and to every downstream consumer).

### Finding Description
`on_accept` dispatches on `request.source`: [1](#0-0) 

```rust
fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
    let source_chain = request.source;
    match source_chain {
        StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
            source: source_chain,
            data: unsafe { String::from_utf8_unchecked(request.body) },
        }),
```

`request.body` is fully attacker-controlled: it is the byte payload of an ISMP `PostRequest` relayed from an EVM chain and delivered through the standard message pipeline — `handle_incoming_message` → `pallet-ismp`'s `execute`/`dispatch_request` handling → the runtime's `ProxyModule::on_accept`, which routes to `pallet_ismp_demo::IsmpModuleCallback::default().on_accept(request)` whenever the destination module id matches `pallet_ismp_demo::PALLET_ID`: [2](#0-1) 

`pallet-ismp-demo` is compiled into and wired up in the production runtimes (`gargantua-runtime`, `nexus-runtime`), not gated behind a test-only feature: [3](#0-2) [4](#0-3) 

Any relayer submitting a proof for a POST request whose `from`/`to` targets this module id (`ModuleId::Pallet(PalletId(*b"ismp-ast"))`) with a source `StateMachine::Evm(_)` and a body containing invalid UTF-8 bytes triggers `String::from_utf8_unchecked` on unchecked, untrusted bytes — this is textbook undefined behavior in Rust: the `String` type's internal invariant (valid UTF-8) is silently broken, and every subsequent operation that relies on that invariant (string slicing, `Display`, RPC/JSON serialization of the event, compiler optimizations that assume valid UTF-8) becomes unsound. Unlike a plain `.expect()`/`.unwrap()` panic (a controlled abort), this is memory-unsafety-class undefined behavior that can manifest as corrupted state, malformed event data surfaced to indexers/relayers, or process crashes depending on optimizer behavior and downstream consumers of the `Event::Request.data` field.

### Impact Explanation
This is directly reachable by any unprivileged relayer delivering a single ISMP message from an EVM source chain — no privileged role required. Because pallet-ismp-demo runs inside the deterministic runtime state-transition function, all collators execute the same faulty code on the same block; a crash or non-deterministic outcome here can halt block production/validation for the chain (via the shared, deterministic on_accept path), or corrupt event data consumed by external indexers and relayer software that assume `Event::Request.data` is valid UTF-8, leading to service disruption for the pallet and its ISMP message-delivery guarantees.

### Likelihood Explanation
High: constructing a malformed UTF-8 body for a `PostRequest` costs nothing and requires only submitting one relayed ISMP message routed to the `ismp-ast` module id with `source = StateMachine::Evm(_)`. No special privileges, races, or governance actions are needed.

### Recommendation
Replace `String::from_utf8_unchecked(request.body)` with a checked conversion (`String::from_utf8(request.body)`), rejecting or lossily-converting (`String::from_utf8_lossy`) the request when the bytes are not valid UTF-8, and return an `IsmpError`/reject the request instead of assuming well-formedness of attacker-controlled bytes — mirroring the fix already applied elsewhere in this codebase for exactly this class of bug (e.g. `modules/utils/serde/src/lib.rs`'s `as_utf8_string::deserialize`, which explicitly rejects malformed untrusted input rather than panicking or invoking UB).

### Proof of Concept
1. As any relayer, construct/relay a valid ISMP `PostRequest` with `source = StateMachine::Evm(<any id>)`, `to = ModuleId::Pallet(PalletId(*b"ismp-ast")).to_bytes()`, and `body` containing an invalid UTF-8 byte sequence (e.g. a lone continuation byte `0x80`).
2. Submit the relayed message through the normal message-handling path so it reaches `pallet-ismp`'s `execute`, which invokes `ProxyModule::on_accept`.
3. Because `request.dest == HostStateMachine` and `pallet_id == pallet_ismp_demo::PALLET_ID`, execution reaches `pallet_ismp_demo::IsmpModuleCallback::on_accept`, which executes `unsafe { String::from_utf8_unchecked(request.body) }` on the malformed bytes, producing a `String` that violates Rust's UTF-8 invariant and is then stored/emitted via `Event::Request`.

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

**File:** parachain/runtimes/gargantua/src/ismp.rs (L406-412)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_accept(request),

```

**File:** parachain/runtimes/gargantua/Cargo.toml (L26-29)
```text
ismp = { workspace = true }
pallet-ismp = { workspace = true }
pallet-fishermen = { workspace = true }
pallet-ismp-demo = { workspace = true }
```

**File:** parachain/runtimes/gargantua/src/lib.rs (L975-977)
```rust
	#[runtime::pallet_index(52)]
	pub type IsmpDemo = pallet_ismp_demo;
	#[runtime::pallet_index(53)]
```
