## Analog Found

### Title
Unbounded-loop extrinsic with a fixed, underestimated declared weight in the production-shipped `pallet-ismp-demo` allows any signed account to stall block production and halt message delivery - (File: `modules/pallets/demo/src/lib.rs`)

### Summary
The Apache Airflow advisory describes a bug class where **example/demo code that was never meant for production was shipped and remained reachable by an authenticated actor, giving them a way to execute far more powerful/dangerous operations than intended.** The direct analog here is `pallet-ismp-demo`, a "simple demo for asset transfer over ISMP" that is explicitly wired into the production Gargantua runtime as `IsmpDemo` at `#[runtime::pallet_index(52)]`, rather than being confined to tests. [1](#0-0) [2](#0-1) 

Its `dispatch_to_evm` extrinsic loops `params.count` times, dispatching one ISMP POST request per iteration, but the entire call is declared with a single fixed weight of `Weight::from_parts(1_000_000, 0)` regardless of `count`: [3](#0-2) 

### Finding Description
`dispatch_to_evm` only requires `ensure_signed(origin)` - any account able to submit a signed extrinsic can call it. Inside, a `for _ in 0..params.count` loop calls `dispatcher.dispatch_request(...)` once per iteration, each of which performs real work (constructing a `PostRequest`, computing its commitment, writing to the offchain DB / MMR via `pallet-ismp`). `params.count` is a `u64` supplied entirely by the caller and is never bounded. Yet the pallet declares the call's weight as the constant `Weight::from_parts(1_000_000, 0)` - completely decoupled from `count`.

This is a classic Substrate weight-benchmarking violation: FRAME's weight-based fee/block-limit system assumes the declared weight upper-bounds the actual execution cost, so the block author can safely pack extrinsics up to `BlockWeights::max_block`. When declared weight is a small constant but actual cost scales linearly (or worse, given repeated MMR/offchain-DB writes) with an attacker-controlled `count`, a single extrinsic can consume far more real execution time/storage than its accounted weight, letting an attacker exceed the intended per-block resource budget while only "paying" for 1,000 units of weight.

### Impact Explanation
Because `IsmpDemo` is compiled into the live Gargantua parachain runtime (the coprocessor that all ISMP messages, BEEFY-verified consensus updates, and Hyperbridge governance actions flow through), an attacker submitting one crafted `dispatch_to_evm(count = <large>)` extrinsic can force a block author to either dramatically overrun the actual weight/time spent executing that block or repeatedly fail to include it, degrading block production. Since Hyperbridge's entire cross-chain messaging pipeline (relaying consensus updates, POST/GET requests, and timeouts to `EvmHost`/`HandlerV2` on destination chains) depends on Gargantua continuing to finalize blocks and accumulate MMR leaves, stalling or repeatedly disrupting block production on this parachain is a route made "unable to deliver messages" for every application built on top of Hyperbridge, not just the demo pallet itself.

### Likelihood Explanation
Exploitation requires nothing beyond a normal signed extrinsic and enough balance to pay the (deliberately mis-declared, cheap) transaction fee - no governance, root, or privileged relayer access is needed, matching the "unprivileged message dispatcher" reachability bar. The bug is trivially discoverable by reading the pallet's `#[pallet::weight]` annotation against its loop body.

### Recommendation
- Remove `pallet-ismp-demo` from the production Gargantua/Nexus runtimes entirely (it explicitly documents itself as a "Simple Demo"), mirroring the Airflow fix of not shipping the vulnerable example in a version reachable by users; or
- If it must remain, bound `params.count` with a hard `MaxCount` constant enforced before the loop, and make the declared weight scale linearly with `count` (e.g. `Weight::from_parts(base, 0).saturating_add(per_item_weight.saturating_mul(params.count))`), consistent with how `transfer`/`get_request` are already limited to a single dispatch per call.

### Proof of Concept
1. An attacker with a funded account submits `IsmpDemo::dispatch_to_evm(EvmParams { module: <any>, destination: <any evm chain id>, timeout: 0, count: u64::MAX })` (or a large finite value tuned to overrun the block weight/time budget).
2. `ensure_signed` succeeds for any account; no further authorization check exists. [4](#0-3) 
3. The extrinsic's declared weight is the constant `Weight::from_parts(1_000_000, 0)`, so the runtime's weight accounting believes this call is cheap, while the `for _ in 0..params.count` loop performs `count` real dispatches through `T::IsmpHost::default().dispatch_request(...)`. [5](#0-4) 
4. Actual execution time vastly exceeds the block's accounted weight budget, causing block production delays/failures on Gargantua and stalling delivery of all in-flight Hyperbridge messages until the condition is mitigated (e.g., via a runtime upgrade removing/patching the pallet).

<br>

Note: this repository's index has size limits, so some files (e.g. full weight-benchmarking configuration for `pallet-ismp-demo`, if any exists outside what was retrieved) may not be fully visible; a Devin session with full repository access could confirm whether any external `WeightInfo` benchmarking wrapper mitigates this before treating the finding as final.

### Citations

**File:** parachain/runtimes/gargantua/src/lib.rs (L975-977)
```rust
	#[runtime::pallet_index(52)]
	pub type IsmpDemo = pallet_ismp_demo;
	#[runtime::pallet_index(53)]
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L207-211)
```rust
impl pallet_ismp_demo::Config for Runtime {
	type Balance = Balance;
	type NativeCurrency = Balances;
	type IsmpHost = Ismp;
}
```

**File:** modules/pallets/demo/src/lib.rs (L216-239)
```rust
		/// Dispatch request to a connected EVM chain.
		#[pallet::weight(Weight::from_parts(1_000_000, 0))]
		#[pallet::call_index(2)]
		pub fn dispatch_to_evm(origin: OriginFor<T>, params: EvmParams) -> DispatchResult {
			let origin = ensure_signed(origin)?;
			let post = DispatchPost {
				dest: StateMachine::Evm(params.destination),
				from: PALLET_ID.to_bytes(),
				to: params.module.0.to_vec(),
				timeout: params.timeout,
				body: b"Hello from polkadot".to_vec(),
			};
			let dispatcher = T::IsmpHost::default();
			for _ in 0..params.count {
				// dispatch the request
				dispatcher
					.dispatch_request(
						DispatchRequest::Post(post.clone()),
						FeeMetadata { payer: origin.clone(), fee: Default::default() },
					)
					.map_err(|_| Error::<T>::TransferFailed)?;
			}
			Ok(())
		}
```
