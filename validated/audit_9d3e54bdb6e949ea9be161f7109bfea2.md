### Title
Unsafe UTF-8 conversion of attacker-controlled cross-chain message body causes memory-safety UB reachable by any unprivileged relayer - (File: modules/pallets/demo/src/lib.rs)

### Summary
CVE-2019-6110 is fundamentally a "client trusts unvalidated attacker-supplied bytes as well-formed output" bug class. The Hyperbridge analog is `IsmpModuleCallback::on_accept` in `pallet-ismp-demo`, which is wired directly into the production Gargantua runtime's `ProxyModule` router. It converts the fully attacker-controlled `PostRequest.body` into a `String` using `unsafe { String::from_utf8_unchecked(...) }` with **no UTF-8 validation**, violating Rust's core safety invariant that every `String` must contain valid UTF-8. [1](#0-0) 

### Finding Description
`on_accept` is the `IsmpModule` callback invoked whenever a POST request destined for the demo pallet's `ModuleId` is delivered:

```rust
StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
    source: source_chain,
    data: unsafe { String::from_utf8_unchecked(request.body) },
}),
``` [2](#0-1) 

`request.body` is arbitrary bytes supplied by whoever dispatched the original ISMP `PostRequest` from an EVM source chain (e.g., any caller of `EvmHost.dispatch(...)` with `to = pallet_ismp_demo::PALLET_ID`). There is no check that these bytes are valid UTF-8 before the unsafe conversion, so a malicious dispatcher can produce a `String` that violates its safety invariant — undefined behavior at the language level, not merely a logic bug.

This callback is reachable from a fully permissionless path: `pallet_ismp::handle_unsigned` is an unsigned extrinsic that anyone can submit with a `RequestMessage` plus a valid membership proof; on successful proof verification it dispatches to `IsmpModule::on_accept` via the runtime's `ProxyModule`, which routes to `pallet_ismp_demo::PALLET_ID` and this exact call. [3](#0-2) [4](#0-3) 

`pallet_ismp_demo` is not a test-only artifact — it is configured and included in the shipped Gargantua parachain runtime: [5](#0-4) 

Because the resulting `String` is invalid per Rust's data-layout contract, any subsequent operation the compiler or standard library performs assuming UTF-8 validity (str indexing, `.chars()`, SIMD-accelerated string routines the optimizer may insert, or SCALE/serde re-encoding by off-chain indexers and RPC clients that decode this event's `data` field as a `String`) is undefined behavior. This can manifest as out-of-bounds memory reads, panics, or corrupted data depending on the exact code path and compiler version — effects entirely analogous to the OpenSSH bug's premise that unsanitized attacker bytes are treated as trustworthy structured output.

### Impact Explanation
A single malicious/careless cross-chain dispatcher can corrupt runtime state in a way that violates Rust's memory-safety guarantees on every Gargantua collator/validator that processes the block, and can crash any off-chain relayer, indexer, or RPC client that decodes the emitted `Event::Request.data` as a `String` (per its SCALE type metadata) using UTF-8-assuming APIs. Because event data flows into indexers and the relayer/tesseract pipeline used to track deliveries, a crash there can stall message indexing and delivery for the affected route — the same "route unable to deliver messages" outcome called out as in-scope impact. The bug is directly reachable by an unprivileged dispatcher/relayer with a single relayed message, no special privileges required.

### Likelihood Explanation
High. `handle_unsigned` is explicitly designed to let "anyone execute ISMP datagrams for free" as long as they hold a valid proof; the source-chain dispatch itself (calling `EvmHost.dispatch` targeting the demo module) is permissionless for any account on the EVM source chain. Triggering the unsafe path only requires setting a non-UTF-8 `body`, which is trivial.

### Recommendation
Replace the unsafe conversion with a fallible one and reject/handle invalid input explicitly, mirroring the pattern already used elsewhere in the codebase (e.g. `String::from_utf8(...).map_err(...)`):

```rust
StateMachine::Evm(_) => {
    let data = String::from_utf8(request.body)
        .map_err(|_| IsmpError::Custom("invalid utf8 in request body".to_string()))?;
    Pallet::<T>::deposit_event(Event::Request { source: source_chain, data });
},
```
More broadly, audit for any other `unsafe { String::from_utf8_unchecked(...) }` usages operating on cross-chain or otherwise externally-controlled byte buffers throughout the pallets.

### Proof of Concept
1. On the EVM source chain, call `EvmHost.dispatch(...)` (permissionless) with `to = pallet_ismp_demo::PALLET_ID` bytes and `body = [0xFF, 0xFE, ...]` (invalid UTF-8).
2. Wait for/act as the relayer and submit `pallet_ismp::handle_unsigned` with the corresponding `RequestMessage` and a valid membership proof for that request.
3. `handlers::handle_incoming_message` verifies the proof and calls `ProxyModule::on_accept`, which routes to `pallet_ismp_demo::IsmpModuleCallback::on_accept`.
4. `unsafe { String::from_utf8_unchecked(request.body) }` constructs an invalid `String` from the attacker's bytes, which is stored in the emitted `Event::Request`, violating Rust's UTF-8 invariant and propagating malformed data to any consumer (node internals, indexers, relayer software) that treats it as valid UTF-8.

### Citations

**File:** modules/pallets/demo/src/lib.rs (L369-377)
```rust
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		let source_chain = request.source;

		match source_chain {
			StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
				source: source_chain,
				data: unsafe { String::from_utf8_unchecked(request.body) },
			}),
			StateMachine::Polkadot(_) | StateMachine::Kusama(_) => {
```

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L207-211)
```rust
impl pallet_ismp_demo::Config for Runtime {
	type Balance = Balance;
	type NativeCurrency = Balances;
	type IsmpHost = Ismp;
}
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L406-412)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_accept(request),

```
