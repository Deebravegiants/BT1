### Title
Bandwidth-gate ("middleware") is enforced on the `on_accept` (POST) path but silently skipped on the `on_response` (GET) path in `ProxyModule` - ([File: parachain/runtimes/gargantua/src/ismp.rs])

### Summary
Gargantua's ISMP module router (`ProxyModule`) enforces the `pallet-bandwidth` metering gate (`BandwidthGate::try_consume`) on every incoming POST request in `on_accept`, but the analogous enforcement documented for `on_response` (incoming GET responses) is never actually invoked. This is the same bug class as the Next.js advisory: an authorization/metering check ("middleware") that correctly guards one route (`on_accept`) but has a matching code path for a logically-equivalent alternate route (`on_response`) that bypasses the check entirely, letting a message reach application logic — and consume resources/service — without passing the intended gate.

### Finding Description
`ProxyModule::on_accept` in `parachain/runtimes/gargantua/src/ismp.rs` explicitly meters every non-purchase POST request against `pallet-bandwidth` before any further processing: [1](#0-0) 

`ProxyModule::on_response`, which handles incoming `GetResponse`s, carries a comment claiming the same enforcement ("Bandwidth gate. Mirrors the request path in `on_accept`... the chain and module that produced the response pay for the bytes they deliver"), but the function body never calls `BandwidthGate::try_consume` (or any gate) — it only checks `dest_chain()` and dispatches straight to the destination module: [2](#0-1) 

This mirrors the Next.js bug class exactly: the matcher/dispatch logic that decides which requests get the security/metering check applied is inconsistent across two logically parallel routes handled by the same "router" (here, `IsmpModule::on_accept` vs `IsmpModule::on_response`), so one path is protected while the functionally-equivalent alternate path is not.

Separately, `pallet-state-coprocessor` (which produces the `GetResponse`s that eventually reach `on_response`) documents its own bandwidth charge on the *request* side only, charging `(req.source, req.from)` when a `GetRequest` is proven — again nothing charges the *response* delivery back into `on_response`: [3](#0-2) 

By contrast, the Nexus runtime's equivalent `ProxyModule::on_response` doesn't claim to enforce the gate at all (no misleading comment), and its `on_accept`/`on_timeout` both consistently apply the deprecated-gateway and bandwidth checks: [4](#0-3) 

This confirms the Gargantua `on_response` path is a genuine gap relative to the documented/intended design (the comment at lines 425-427 states the gate is supposed to mirror `on_accept`), not an intentional exemption.

### Impact Explanation
`pallet-bandwidth` is the economic gate that makes cross-chain messaging metered/paid on Gargantua (governance-managed tiers, purchases, treasury withdrawals — see `modules/pallets/bandwidth`). Any code path that delivers a message to a destination module without going through `try_consume` lets that traffic bypass the metering entirely — i.e., unlimited free delivery of `GetResponse` payloads to on-chain modules regardless of whether the responding app/chain has any bandwidth allowance. Because the destination module (`pallet_ismp_demo` or any future GET-consuming module) executes with weight/storage cost on Gargantua for every delivered response, this is an authorization/billing bypass: the "unauthorized app action" is the module receiving and processing a paid-for-but-unpaid delivery, and cumulatively it undermines the entire billing model the protocol relies on for GET-based cross-chain state reads.

### Likelihood Explanation
GET responses are delivered whenever a relayer submits a valid state-membership proof for a previously dispatched `GetRequest` (a routine, permissionless relayer operation via `HandlerV2.handleGetResponses` / pallet-ismp equivalents). No special privilege is needed to trigger `on_response` — any relayer completing normal GET-request/response flows exercises the unmetered path on every single call, making the bypass 100% reliably reachable, not a rare edge case.

### Recommendation
Add the same `BandwidthGate::try_consume` enforcement to `ProxyModule::on_response` in `parachain/runtimes/gargantua/src/ismp.rs` that already exists in `on_accept`, keyed the same way the comment describes (source chain / responding module, sized by the encoded response payload), gated behind the same `#[cfg(not(feature = "no-bandwidth"))]` flag used elsewhere. Additionally, audit all other `IsmpModule` callback implementations (`on_timeout`, and any other runtime's `ProxyModule`) for the same "documented-but-missing" enforcement pattern to ensure metering/authorization is applied uniformly across every dispatch route, not just the primary one.

### Proof of Concept
1. An application on Gargantua dispatches a `GetRequest` to a remote chain (bandwidth is not charged for issuing the GET itself in this code path, only for POST ingress and for `GetRequestsWithProof` handled by `pallet-state-coprocessor`).
2. A relayer submits the corresponding `GetResponse` with a valid membership proof through the normal handler pipeline.
3. `pallet-ismp`'s response handler resolves `router.module_for_id(...)` to `ProxyModule` and calls `on_response(response)`.
4. Execution reaches `parachain/runtimes/gargantua/src/ismp.rs:424-441` — no call to `BandwidthGate::try_consume` occurs anywhere in this function, unlike the equivalent `on_accept` path (lines 381-396), so the delivery is processed for free regardless of the responding chain/module's `pallet-bandwidth` allowance, silently bypassing the protocol's metering "middleware."

### Citations

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

**File:** modules/pallets/state-coprocessor/src/lib.rs (L60-64)
```rust
		/// Bandwidth gate that meters per-app data consumption. The
		/// coprocessor charges `max(sum(keys.len()) + context.len(), 32)`
		/// bytes per `GetRequest` against `(req.source, req.from)` before
		/// any state proof work — fails fast for apps without allowance.
		type BandwidthGate: pallet_bandwidth::BandwidthGate;
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L362-419)
```rust
impl IsmpModule for ProxyModule {
	fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
		// Permanently reject any request originating from a deprecated TokenGateway
		// deployment, regardless of destination. This short-circuits both the
		// forwarding path (dest != host) and the locally-dispatched path below.
		if is_deprecated_token_gateway(&request.from) {
			return Err(anyhow!(
				"rejecting request from deprecated TokenGateway address {:?} on {:?}",
				request.from,
				request.source,
			));
		}

		// Bandwidth gate. Always-enforce; skipped for purchase messages so the
		// recharge flow itself doesn't need bandwidth.
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

		if request.dest != HostStateMachine::get() {
			Ismp::dispatch_request(
				Request::Post(request),
				FeeMetadata::<Runtime> { payer: [0u8; 32].into(), fee: Default::default() },
			)?;
			return Ok(Weight::from_parts(0, 0));
		}

		let pallet_id =
			ModuleId::from_bytes(&request.to).map_err(|err| Error::Custom(err.to_string()))?;

		match pallet_id {
			id if id == ModuleId::Pallet(pallet_bandwidth::pallet::PALLET_BANDWIDTH) =>
				pallet_bandwidth::Pallet::<Runtime>::default().on_accept(request),
			pallet_hyper_fungible_token::PALLET_ID =>
				pallet_hyper_fungible_token::Pallet::<Runtime>::default().on_accept(request),
			_ => Err(anyhow!("Destination module not found")),
		}
	}

	fn on_response(&self, response: GetResponse) -> Result<Weight, anyhow::Error> {
		if response.dest_chain() != HostStateMachine::get() {
			return Ok(Weight::from_parts(0, 0));
		}

		Err(anyhow!("Destination module not found"))
	}
```
