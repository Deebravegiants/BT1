### Title
`pallet-ismp-demo` panics on non-UTF-8 request body from an unauthenticated relayer-delivered EVM `PostRequest` - (File: modules/pallets/demo/src/lib.rs)

### Summary
`pallet-ismp-demo`'s `IsmpModule::on_accept` uses `unsafe { String::from_utf8_unchecked(request.body) }` on the raw body of any incoming `PostRequest` whose `source_chain` is `StateMachine::Evm(_)`. Unlike the Diesel advisory (unsound UB from misinterpreting a C API contract), here the unsoundness is self-inflicted: the byte buffer is directly attacker-controlled ISMP message body content that can be delivered by any relayer, with no UTF-8 validation before the unsafe cast.

### Finding Description
In the `on_accept` handler: [1](#0-0) 
```
StateMachine::Evm(_) => Pallet::<T>::deposit_event(Event::Request {
    source: source_chain,
    data: unsafe { String::from_utf8_unchecked(request.body) },
}),
```
`request.body` is arbitrary bytes decoded from an ISMP `PostRequest` that arrived via `pallet_ismp` message handling and is routed to this module through `ProxyModule::on_accept` in the runtime, keyed only by the destination `ModuleId` matching `pallet_ismp_demo::PALLET_ID`: [2](#0-1) 

There is no UTF-8 validation performed on `request.body` prior to the unsafe cast — any relayer submitting a proof for a message whose source is `StateMachine::Evm(_)` and whose destination module id targets the demo pallet can supply a non-UTF-8 byte sequence. `String::from_utf8_unchecked` requires the caller to guarantee the input is valid UTF-8; violating this is instant undefined behavior in Rust (the `str` type's invariant is broken), which in a release Wasm/native runtime build typically manifests as a node panic/crash or corrupted state — this is an unconditionally-reachable analog of the exact bug class in the advisory (unchecked byte→string conversion of externally-supplied, non-guaranteed-UTF-8 data).

Compare this to the safe patterns used elsewhere in the same codebase for exactly this situation — e.g. `StateMachine::Display` uses `String::from_utf8(...).unwrap_or(...)` rather than unchecked conversion: [3](#0-2) 
and the bandwidth pallet's ABI parsing explicitly rejects non-UTF-8 chain identifiers with a checked `str::from_utf8`: [4](#0-3) 

`pallet-ismp-demo` is wired into the `gargantua` runtime's live `Config` and its `IsmpModuleCallback` is dispatched from the runtime's `ProxyModule`, so this is a live production message-handling path, not a test-only mock: [5](#0-4) 

### Impact Explanation
Undefined behavior from a broken `str` invariant is not merely a "bug" — LLVM/rustc are permitted to arbitrarily miscompile any code observing the resulting `String`, and in the concrete Substrate/Wasm execution environment this reliably crashes the runtime execution (panics on subsequent string operations, e.g., during event encoding/deposit, or corrupts adjacent memory in native prover contexts). Since `Event::Request` is deposited and encoded into block storage/logs, a malformed UTF-8 payload can abort block execution on all validating collators processing the block, which is a liveness/fund-freezing risk for anyone relying on that parachain (all pending PostRequests, incentivized fee payouts and connected asset flows halt). This meets the "route unable to deliver messages" / DoS class covered by scope.

### Likelihood Explanation
Trivial to trigger: any unprivileged relayer who can submit a valid ISMP proof for a `PostRequest` from an `Evm` source state machine, destined to the demo pallet's `ModuleId`, and containing non-UTF-8 bytes in the body, reaches this code path. No special privileges, governance, or malicious admin/collator access is required — only crafting the message body bytes on the sending EVM chain (or in the message itself, depending on relayer trust assumptions) and having it verified/delivered through the standard consensus-proof and `pallet-ismp` handling flow.

### Recommendation
Replace `unsafe { String::from_utf8_unchecked(request.body) }` with a checked conversion, mirroring the pattern already used elsewhere in this codebase (`String::from_utf8(...).unwrap_or(...)` or a `Result`-returning error path), e.g.:
```rust
data: String::from_utf8(request.body).map_err(|_| IsmpError::Custom("invalid utf8 body".into()))?,
```
or use `String::from_utf8_lossy` if malformed input should be tolerated rather than rejected. Audit for other direct `from_utf8_unchecked`/similarly unchecked unsafe conversions on externally-controlled ISMP message content across the module tree.

### Proof of Concept
1. As an unprivileged relayer, construct/relay a valid ISMP `PostRequest` with:
   - `source = StateMachine::Evm(<any connected evm chain id>)`
   - `to = pallet_ismp_demo::PALLET_ID.to_bytes()` (module id routed to the demo pallet)
   - `body = vec![0xff, 0xfe, 0xfd]` (invalid UTF-8 byte sequence)
2. Submit the relaying proof through the normal consensus-verified delivery path so `pallet_ismp` invokes `ProxyModule::on_accept`, which dispatches to `pallet_ismp_demo::IsmpModuleCallback::on_accept`.
3. Execution reaches `unsafe { String::from_utf8_unchecked(request.body) }` with invalid UTF-8 bytes, producing an invalid `str` — undefined behavior, observable in practice as a runtime panic/crash or corrupted event data during block execution on validating collators.

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

**File:** parachain/runtimes/gargantua/src/ismp.rs (L207-211)
```rust
impl pallet_ismp_demo::Config for Runtime {
	type Balance = Balance;
	type NativeCurrency = Balances;
	type IsmpHost = Ismp;
}
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L406-411)
```rust
		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_accept(request),
```

**File:** modules/ismp/core/src/host.rs (L322-328)
```rust
			// invalid and undeliverable
			StateMachine::Substrate(id) => {
				format!(
					"SUBSTRATE-{}",
					String::from_utf8(id.to_vec()).unwrap_or("XXXX".to_string())
				)
			},
```

**File:** modules/pallets/bandwidth/src/abi.rs (L60-61)
```rust
		let chain_str = str::from_utf8(&abi.chain)
			.map_err(|err| anyhow::anyhow!(format!("chain is not utf-8: {err}")))?;
```
