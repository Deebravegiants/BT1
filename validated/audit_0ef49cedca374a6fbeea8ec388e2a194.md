### Title
Bandwidth-gate comment claims parity with `on_accept`, but `on_response` in gargantua's `ProxyModule` never calls `try_consume` — GET responses bypass metering entirely - (File: `parachain/runtimes/gargantua/src/ismp.rs`)

### Summary
The bullfrog advisory shows a filter that is faithfully enforced on one delivery path (UDP DNS) but silently skipped on an equivalent alternate path (TCP DNS) that carries the exact same payload, letting an attacker route around the control simply by choosing the unenforced path. The Hyperbridge analog is `pallet-bandwidth`'s metering gate: `on_accept` (POST requests) always calls `BandwidthGate::try_consume` to charge bytes against an app's prepaid allowance, but `on_response` (GET responses) — the sibling delivery path that the code comment explicitly claims "mirrors the request path" — never calls `try_consume` at all.

### Finding Description
`pallet-bandwidth` meters "outbound traffic per `(source chain, app)`" and is documented as a hook "the ISMP router consults on every inbound request from a source chain," rejecting messages "when the gate is empty" [1](#0-0) . The gate itself, `BandwidthGate::try_consume`, drains bytes from `Allowance` and can reject with `NoAllowance`/`Insufficient` [2](#0-1) .

In gargantua's `ProxyModule::on_accept`, this gate is enforced on every non-purchase `PostRequest`: the ABI-encoded request length is measured and charged against `request.source`/`request.from` before the request is routed to a module or forwarded onward [3](#0-2) .

`ProxyModule::on_response`, which handles `GetResponse` delivery, carries a comment claiming the same enforcement — "Bandwidth gate. Mirrors the request path in `on_accept`: the chain and module that produced the response pay for the bytes they deliver" — but the function body that follows contains no call to `try_consume`, `BandwidthGate`, or any byte accounting at all. It only checks `response.dest_chain()` and dispatches to the destination module: [4](#0-3) .

Because `GetResponse` and `PostRequest` are both attacker/app-reachable delivery vehicles into the same `IsmpModule` interface (and GET responses carry a `body`/`get.from` module identifier exactly analogous to a POST's `from`/`body`), any app that wants to move data through Hyperbridge without paying for bandwidth has a second, unmetered path: dispatch the payload as a `GetResponse` instead of a `PostRequest`. This is structurally identical to the bullfrog bug — the enforcement point exists and is documented as symmetric across both paths, but only one of the two equivalent delivery mechanisms actually invokes the check.

### Impact Explanation
The bandwidth subscription model exists specifically so that "the allowance drains as it sends messages" and "the gate silently passes messages until the balance is exhausted" [5](#0-4) . Skipping the gate on the response path means an app can deliver unlimited byte volume through Hyperbridge for free by using GET responses, undermining the entire metering/billing invariant that the bandwidth pallet enforces on the request path — a direct loss of protocol fee revenue and an unmetered-resource / DoS-adjacent channel (unbounded state trie growth via committed GET responses without ever draining a paid subscription). This is a sandbox/quota bypass on a protocol economic control reachable from any dispatched message, matching Medium severity of the analog advisory.

### Likelihood Explanation
No privileged access is required — any app/module that can already dispatch or receive ISMP `GetResponse` traffic on the destination chain (nexus/gargantua) can exploit this simply by preferring GET/response-shaped delivery over POST for its payloads. The code path is on by default (bandwidth pallet compiled in unless the `no-bandwidth` feature is set) [6](#0-5) , so the gap is live in the default runtime configuration.

### Recommendation
Add the same `BandwidthGate::try_consume` call in `ProxyModule::on_response` that exists in `on_accept`, charging `response.get.source`/`response.get.from` for the encoded response size before dispatch, so both delivery paths are metered symmetrically as the code comment already claims.

### Proof of Concept
Conceptual PoC (would need a background Devin session with repo access to execute against a testnet):
1. Deploy/point an app at gargantua with `pallet-bandwidth` active and no purchased allowance (or an exhausted one).
2. Attempt to deliver a large payload via `Ismp::dispatch_request` as a `PostRequest` — observe rejection via `BandwidthGate::try_consume` (`NoAllowance`/`Insufficient`) as enforced in `on_accept`.
3. Deliver the same payload volume via the `GetResponse` path (module answering a GET query with a large response body) targeting the same app/source — observe that `ProxyModule::on_response` dispatches it to the destination module without any call into `pallet_bandwidth`, i.e., the byte allowance is never touched and delivery succeeds regardless of subscription state.

### Citations

**File:** docs/content/developers/evm/bandwidth/overview.mdx (L8-10)
```text
Hyperbridge meters outbound traffic per `(source chain, app)`. Instead of paying a protocol fee on every dispatch, an app pre-pays for a tier and earns a byte allowance that drains as it sends messages. The allowance is enforced by the **bandwidth gate** on Hyperbridge — a hook the ISMP router consults on every inbound request from a source chain. When the gate is empty, the message is rejected.

Bandwidth is sold per **tier** (a byte budget × a time window) and per **month** (a multiplier on both). Purchases are made from any source chain by calling `purchase()` on the [`BandwidthManager`](https://github.com/polytope-labs/hyperbridge/blob/main/evm/src/apps/BandwidthManager.sol) contract; the contract dispatches a credit message to [`pallet-bandwidth`](https://github.com/polytope-labs/hyperbridge/blob/main/modules/pallets/bandwidth/src/lib.rs) on Hyperbridge, which mints a new subscription for the target `(chain, app)`.
```

**File:** docs/content/developers/evm/bandwidth/overview.mdx (L16-16)
```text
Bandwidth swaps that model for a subscription. An app buys a tier once, the pallet tracks the remaining byte balance, and the gate silently passes messages until the balance is exhausted. There's no per-message fee path on dispatch — the cost was paid at purchase time.
```

**File:** modules/pallets/bandwidth/src/lib.rs (L509-535)
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

```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L376-396)
```rust
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Bandwidth gate. Always-enforce unless the `no-bandwidth` flag
		// is set; skipped for purchase messages so the recharge flow
		// itself doesn't need bandwidth. With the flag on the gate is a
		// no-op and this block is compiled out entirely.
		#[cfg(not(feature = "no-bandwidth"))]
		if !pallet_bandwidth::Pallet::<Runtime>::is_purchase_message(&request) {
			let bytes = ismp::abi::encode_post_request(&request).len() as u32;
			<pallet_bandwidth::Pallet<Runtime> as pallet_bandwidth::BandwidthGate>::try_consume(
				&request.source,
				&request.from,
				bytes,
			)
			.map_err(|err| {
				anyhow!(
					"bandwidth gate: {err} (source={:?}, from={:x?})",
					request.source,
					request.from
				)
			})?;
		}
```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L424-441)
```rust
	fn on_response(&self, response: GetResponse) -> Result<Weight, anyhow::Error> {
		// Bandwidth gate. Mirrors the request path in `on_accept`: the chain
		// and module that produced the response pay for the bytes they
		// deliver. Compiled out when the `no-bandwidth` flag is on.
		if response.dest_chain() != HostStateMachine::get() {
			return Ok(Weight::from_parts(0, 0));
		}

		let dest = &response.get.from;

		let pallet_id = ModuleId::from_bytes(dest).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			pallet_ismp_demo::PALLET_ID =>
				pallet_ismp_demo::IsmpModuleCallback::<Runtime>::default().on_response(response),
			_ => Err(anyhow!("Destination module not found")),
		}
	}
```

**File:** parachain/runtimes/gargantua/Cargo.toml (L126-134)
```text
default = ["std"]
# Negatively-biased flag for `pallet-bandwidth`. Off by default, so the
# `Bandwidth` pallet is part of `construct_runtime!` and the bandwidth
# gate is wired into the ISMP router (`on_accept` / `on_response`).
# Turning this flag ON strips the pallet from the runtime: the `Bandwidth`
# entry is dropped, the gate becomes a no-op `BandwidthGate`, and none of
# the pallet's extrinsics are exposed. Release builds for testnet
# deployments enable this — see `scripts/build_release_runtime.sh`.
no-bandwidth = []
```
