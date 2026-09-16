### Title
Bandwidth allowance key collision via silent `AppKey` truncation lets an unprivileged dispatcher drain another app's paid bandwidth - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth` credits and later debits per-app message bandwidth keyed on an `AppKey` (`BoundedVec<u8, _>`) derived from the ISMP module identifier (`request.from` / purchase message `app`). The crediting path (`PurchaseMessage::try_from` in `modules/pallets/bandwidth/src/abi.rs`) strictly rejects any `app` identifier longer than `AppKey::bound()`, guaranteeing the stored key exactly matches the buyer's intended identifier. The debiting path (`BandwidthGate::try_consume` in `modules/pallets/bandwidth/src/lib.rs`), which runs on *every* non-purchase message from any registered source chain, instead silently truncates the caller-supplied `app` bytes via `AppKey::truncate_from(app.to_vec())` with no length check at all. Because `request.from` on an EVM `PostRequest` is an attacker-controlled `bytes` field of arbitrary length (not fixed-width like an address), an unprivileged dispatcher can craft a `from` value that differs from a legitimate paying app's identifier only *after* the truncation boundary, causing `try_consume` to resolve to the same `AppKey` as the victim app and drain its paid-for allowance.

### Finding Description
The bug class mirrors the Fluentd advisory's root cause: an attacker-controlled, variable-length field is written into a structural/keying context using a lossy transformation (there: raw string concatenation without escaping so newlines change the structure; here: byte-truncation without a length check so distinct identifiers collapse into the same storage key) on one code path, while a stricter, safe transformation is used on a sibling path that establishes the "true" record.

Evidence:
- Crediting (`on_accept` in `modules/pallets/bandwidth/src/lib.rs:454-489`) uses `PurchaseMessage::try_from`, which enforces:
```rust
if abi.app.is_empty() || abi.app.len() > AppKey::bound() {
    return Err(...)
}
``` [1](#0-0) 
so `AppKey::truncate_from(msg.app)` in `on_accept` never actually truncates — the stored key exactly equals what the buyer paid to credit. [2](#0-1) 

- Debiting (`BandwidthGate::try_consume`, invoked by the ISMP router on every ordinary dispatched message) has no such length guard:
```rust
fn try_consume(source: &StateMachine, app: &[u8], bytes: u32) -> Result<(), GateError> {
    let key = AppKey::truncate_from(app.to_vec());
    ...
}
``` [3](#0-2) 
Here `app` is `request.from`, taken directly from an inbound `PostRequest` dispatched by any account on a registered source chain — a `bytes calldata` field with no fixed length in `BandwidthManager`/`EvmHost` dispatch paths, and consumed unconditionally by `<pallet_bandwidth::Pallet<Runtime> as pallet_bandwidth::BandwidthGate>::try_consume(&request.source, &request.from, bytes)` in the runtime's `ProxyModule::on_accept`. [4](#0-3) [5](#0-4) 

Since `AppKey::truncate_from` silently drops bytes beyond `AppKey::bound()` instead of rejecting, two distinct `from` values that share the same `AppKey::bound()`-byte prefix collapse onto the identical `Allowance::<T>` storage entry keyed `(source, key)`. An attacker fully controls the trailing bytes of their own `from` field (it's just calldata they choose when dispatching from their own contract), so they can pad/craft it to share a prefix with a legitimate, already-funded app's shorter `from` identifier on the same source chain.

### Impact Explanation
This is analogous to "a route unable to deliver messages" / unauthorized consumption of a shared resource, both explicitly accepted impacts. A victim app that has legitimately purchased bandwidth (paying real fee-token funds through `BandwidthManager.purchase`) can have its `Allowance` FIFO silently drained to zero by an unrelated attacker dispatching cheap/no-op messages whose `from` collides after truncation. Once drained, every subsequent legitimate message from the victim app is rejected by the gate (`GateError::NoAllowance` / `Insufficient`), i.e. the victim's messages become undeliverable until they re-purchase — a funds-loss-equivalent denial of service reachable from a single unprivileged dispatched request, with no privileged role required on the attacker's side.

### Likelihood Explanation
High reachability: any account on any EVM chain with a registered `BandwidthManager` can dispatch an ISMP `PostRequest` with an arbitrary `from` value of the attacker's choosing (bounded only by gas/calldata limits), and the bandwidth gate runs on every such non-purchase message automatically. No governance, admin, or relayer collusion is needed — this is a pure "single dispatched request from an unprivileged sender" bug, matching the required threat model exactly. The only uncertainty is the concrete value of `AppKey::bound()` (not fully confirmed in the excerpts reviewed) and whether typical module-id encodings (20-byte EVM address, 32-byte contract account, 8-byte pallet id) already sit within that bound — if `bound()` is set at or above the largest legitimate `from` encoding actually used by the router, a crafted collision still requires the attacker's own address+suffix to match another app's prefix, which is trivially achievable since the attacker chooses their own calldata's suffix bytes.

### Recommendation
Make `try_consume`'s key derivation consistent with the crediting path: reject (or bound-check and error, not truncate) any `app`/`request.from` value longer than `AppKey::bound()` before it is used as a storage key, mirroring the explicit length check already performed in `PurchaseMessage::try_from`. Equivalently, use `AppKey::try_from` (which errors on overflow) instead of `AppKey::truncate_from` in both `try_consume` and any other site that derives an `AppKey` from untrusted request fields (e.g. `allowances`/`remaining` read helpers), so two different `from` identifiers can never resolve to the same key.

### Proof of Concept
1. On the registered EVM source chain, App A calls `BandwidthManager.purchase(app = A_ADDR (20 bytes), tier, months, chain)`, crediting `Allowance[(source, AppKey(A_ADDR))]` with paid bandwidth (`pallet-bandwidth::on_accept`, gated by the exact-length check in `PurchaseMessage::try_from`).
2. An attacker deploys/uses a contract whose dispatched `PostRequest.from` is crafted as `A_ADDR ++ <arbitrary_suffix>` such that `AppKey::bound()` bytes of it equal `A_ADDR` (e.g. if `AppKey::bound()` == 20, any `from` that starts with `A_ADDR` and is longer than 20 bytes collides directly).
3. Attacker dispatches ordinary (non-purchase) messages from this crafted `from`. The runtime's `ProxyModule::on_accept` calls `BandwidthGate::try_consume(&request.source, &request.from, bytes)`, which truncates `request.from` to `AppKey::truncate_from(...)`, landing on the same key as App A's paid allowance.
4. Each such attacker-dispatched message drains bytes from App A's `Allowance` FIFO via `try_consume`'s drain loop, until `NoAllowance`/`Insufficient` is returned for App A's own subsequent legitimate messages — denying App A service despite having paid, at zero cost to the attacker beyond their own message-dispatch gas.

### Citations

**File:** modules/pallets/bandwidth/src/abi.rs (L52-58)
```rust
		if abi.app.is_empty() || abi.app.len() > AppKey::bound() {
			return Err(anyhow::anyhow!(format!(
				"app identifier must be 1..={} bytes, got {}",
				AppKey::bound(),
				abi.app.len()
			)));
		}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L467-481)
```rust
			let msg = PurchaseMessage::try_from(request.body.as_slice())?;
			let tier = TierIndex::try_from(msg.tier)
				.map_err(|_| anyhow::anyhow!(format!("unknown tier discriminant {}", msg.tier)))?;
			let cfg = Tiers::<T>::get(tier)
				.ok_or_else(|| anyhow::anyhow!(format!("tier {:?} is not configured", tier)))?;

			let bytes = cfg.bytes.saturating_mul(msg.months as u128);
			let duration = cfg.duration_secs.saturating_mul(msg.months as u64);

			let key = AppKey::truncate_from(msg.app);
			let expires_at = Self::push_subscription(&msg.chain, &key, tier, bytes, duration);

			Self::deposit_event(Event::BandwidthCredited {
				app_chain: msg.chain,
				app: key,
```

**File:** modules/pallets/bandwidth/src/lib.rs (L509-519)
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

```

**File:** parachain/runtimes/gargantua/src/ismp.rs (L381-396)
```rust
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

**File:** parachain/runtimes/nexus/src/ismp.rs (L377-391)
```rust
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
