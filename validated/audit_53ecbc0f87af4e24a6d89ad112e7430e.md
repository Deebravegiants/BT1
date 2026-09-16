Found it: `try_consume` (and `is_purchase_message`'s sibling `allowances`) silently truncate the caller-supplied `app` identifier to 32 bytes via `AppKey::truncate_from`, exactly the "long-string-hides-the-real-suffix" bug class in the Zen report — the visible/matched prefix is trusted while the differentiating tail is silently dropped.

### Title
Bandwidth gate silently truncates the `app` identifier to 32 bytes, letting distinct apps collide and steal/drain each other's prepaid bandwidth allowance - (File: modules/pallets/bandwidth/src/lib.rs)

### Summary
`pallet-bandwidth`'s `BandwidthGate::try_consume` and the read-only `allowances`/`remaining` helpers key the `Allowance` storage map by `AppKey::truncate_from(app.to_vec())` [1](#0-0) , where `AppKey = BoundedVec<u8, ConstU32<32>>` [2](#0-1) . `truncate_from` silently drops any bytes beyond the first 32 rather than rejecting the input, just as the Zen browser silently drops everything past the visible prefix of a long hostname. Any two `app` byte-strings that share the same first-32-byte prefix collapse to the same storage key and therefore the same bandwidth allowance bucket.

### Finding Description
The gate is invoked from the ISMP router with `request.from`, the attacker-controlled module identifier taken directly from an untrusted, relayed cross-chain POST request: `<pallet_bandwidth::Pallet<Runtime> as pallet_bandwidth::BandwidthGate>::try_consume(&request.source, &request.from, bytes)` [3](#0-2) . `request.from` is an arbitrary `Vec<u8>` with no length bound enforced before reaching the gate — the pallet's own `PostRequest` dispatcher type declares `from: Vec<u8>` with no size restriction [4](#0-3) .

Inside `try_consume`, `AppKey::truncate_from(app.to_vec())` builds the storage key by truncating to 32 bytes, without any check that the input was already ≤32 bytes [5](#0-4) . The credit path (`on_accept`, used when a real `BandwidthManager` purchase message arrives) does the same truncation on `msg.app`, an ABI-decoded, purchaser-controlled byte string, before crediting a subscription: `let key = AppKey::truncate_from(msg.app);` [6](#0-5) .

This is the direct analog of the Zen bug: the system displays/keys on only the first N bytes ("prefix") of an identifier while treating the whole identifier as authoritative, so an attacker can craft a long `from`/`app` identifier that shares a 32-byte prefix with a legitimate app's identifier (or its own registered manager's address padded/extended) while being a functionally distinct identity to the rest of the protocol. Notably the project's own test suite already recognized and fixed this exact class for the purchase-message `PurchaseMessage.app` field parsed at ABI-decode time, explicitly rejecting inputs longer than the `AppKey` bound instead of truncating them [7](#0-6)  — but that fix only covers the decode-time ABI struct; the actual storage-key derivation in `try_consume`/`on_accept`/`allowances` still uses the silently-truncating `truncate_from`, so the underlying collision is not eliminated at the point that matters (the gate itself).

### Impact Explanation
Two apps whose module identifiers agree on the first 32 bytes but differ afterward are indistinguishable to the gate. This lets an attacker-controlled module (reachable via the unprivileged relayed-message dispatch path, since `request.from` is fully attacker-chosen on the source chain and only 32-byte-prefix-checked here) drain another app's prepaid bandwidth allowance by presenting a `from` value that shares the victim's 32-byte prefix — a real theft of prepaid, already-paid-for resources (bandwidth bytes purchased by another party). It can also be used to force `SubscriptionEvicted` on a victim's FIFO list (since the same `(chain, key)` bucket is shared), causing legitimate credited bandwidth to be evicted/lost. Because the credit path and consumption path both compute the same truncated key, an attacker can also engineer a scenario where a legitimate purchase for one app is silently redirected to (or shared with) a collision app of the attacker's own crafting.

### Likelihood Explanation
Reachable directly from a single relayed/dispatched ISMP request: the router calls the gate with the caller-controlled `request.from` on every non-purchase message [8](#0-7) ; `request.from` originates on the source chain and is not length-restricted before it reaches `pallet-bandwidth`. No privileged role, governance, or malicious node/collator/peer is required — an ordinary application/message dispatcher on a connected chain (an "unprivileged message dispatcher" per scope) can pick a colliding `from` value.

### Recommendation
Reject (rather than silently truncate) any `app`/`from` identifier longer than the `AppKey` bound at every point that derives the storage key — `try_consume`, `on_accept`'s `msg.app` handling, and the `allowances`/`remaining` helpers — mirroring the fix already applied to `PurchaseMessage.app` decoding. Use `AppKey::try_from(app.to_vec())` and propagate a `GateError`/`Error` variant instead of `AppKey::truncate_from`.

### Proof of Concept
1. Attacker registers/controls a module on a connected chain whose identifier is `victim_app_bytes[0..32] || extra_bytes` (33+ bytes), sharing the victim legitimate app's first 32 bytes.
2. Victim purchases bandwidth normally; `on_accept` computes `key = AppKey::truncate_from(victim_app_bytes)` (exactly 32 bytes, unchanged) and credits `Allowance[(app_chain, key)]` [6](#0-5) .
3. Attacker dispatches a POST request with `request.from = victim_app_bytes[0..32] || extra_bytes`; the router calls `try_consume(&request.source, &request.from, bytes)` [3](#0-2) .
4. `try_consume` computes `key = AppKey::truncate_from(app.to_vec())`, which collapses to the same 32-byte key as the victim's, and drains the victim's prepaid `Allowance` bucket for attacker's own message bytes [1](#0-0) .

### Citations

**File:** modules/pallets/bandwidth/src/lib.rs (L474-481)
```rust
			let duration = cfg.duration_secs.saturating_mul(msg.months as u64);

			let key = AppKey::truncate_from(msg.app);
			let expires_at = Self::push_subscription(&msg.chain, &key, tier, bytes, duration);

			Self::deposit_event(Event::BandwidthCredited {
				app_chain: msg.chain,
				app: key,
```

**File:** modules/pallets/bandwidth/src/lib.rs (L510-516)
```rust
	fn try_consume(
		source: &ismp::host::StateMachine,
		app: &[u8],
		bytes: u32,
	) -> Result<(), GateError> {
		let key = AppKey::truncate_from(app.to_vec());
		if Allowlist::<T>::contains_key(source, &key) {
```

**File:** modules/pallets/bandwidth/src/types.rs (L11-13)
```rust
/// Recipient app identifier on the credit chain. Bounded so it fits
/// inline in storage; usually a 20-byte EVM address right-padded.
pub type AppKey = BoundedVec<u8, ConstU32<32>>;
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L362-391)
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
```

**File:** modules/ismp/core/src/dispatcher.rs (L23-36)
```rust
/// Simplified POST request, intended to be used for sending outgoing requests
#[derive(Clone)]
pub struct DispatchPost {
	/// The destination state machine of this request.
	pub dest: StateMachine,
	/// Module identifier of the sending module
	pub from: Vec<u8>,
	/// Module identifier of the receiving module
	pub to: Vec<u8>,
	/// Relative from the current timestamp at which this request expires in seconds.
	pub timeout: u64,
	/// Encoded request body
	pub body: Vec<u8>,
}
```

**File:** modules/pallets/testsuite/src/tests/pallet_bandwidth.rs (L532-547)
```rust
/// `app` is stored as an `AppKey`, so bytes past its bound are not a longer identifier — they
/// silently disappear. The tier price is flat regardless of body length, so a purchase carrying
/// them is paying the same for a message that got longer for no reason; reject it at decode time
/// instead of truncating.
#[test]
fn purchase_rejects_app_identifier_over_the_bound() {
	new_test_ext().execute_with(|| {
		jump_to(T0);
		register_manager(APP_CHAIN);
		configure_tier(TIER1, TIER1_BYTES, MONTH_SECS);

		dispatch(purchase_request_with_app(vec![0xBB; AppKey::bound() + 1]))
			.expect_err("app identifier longer than AppKey must be rejected at decode time");
		assert_eq!(sub_count(APP_CHAIN), 0);
	});
}
```
