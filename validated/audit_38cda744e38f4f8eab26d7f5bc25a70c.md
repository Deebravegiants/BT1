Based on my research, I found a valid analog vulnerability in `pallet-bandwidth`.

### Title
Griefer can force-evict a victim's paid bandwidth subscription via FIFO-cap eviction, permanently freezing prepaid funds - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
The bandwidth subscription ledger is a per-`(app_chain, app)` FIFO list capped at `MAX_SUBSCRIPTIONS = 1024`. Any account can call `purchase()` on `BandwidthManager.sol` and credit a subscription for *any* `(app_chain, app)` pair — the credit target is taken from the message body (`app_chain`, `app`), not tied to the caller's own identity. When the list is full, `push_subscription` silently evicts the oldest live subscription and emits `SubscriptionEvicted`, without any compensation or refund path.

### Finding Description
`push_subscription` in `modules/pallets/bandwidth/src/lib.rs` unconditionally evicts the head of a full 1024-entry `SubscriptionList` to make room for a new purchase: [1](#0-0) 

Because `Allowance` is keyed by `(app_chain, app)` taken from the purchase message payload — independent of `request.source` or the caller — anyone able to fund the cheapest tier can direct 1024 low-value purchases at a target app's `(app_chain, app)` bucket: [2](#0-1) [3](#0-2) 

This mirrors the M-18 pattern: a first-come-first-served, shared, capped resource (the LiquidityReserve's single cooldown slot vs. here a bounded FIFO queue) that an unprivileged actor can fill/overwrite with low-cost transactions, permanently displacing another user's already-paid-for entitlement with no batching or reservation logic to protect it.

### Impact Explanation
A victim who has already paid for bandwidth (their tokens are spent and cannot be refunded — there is no `Withdraw`-based user refund path for evicted subscriptions, only an admin `force_credit` escape hatch) can have their still-unused, unexpired subscription evicted before it is ever drained. `SubscriptionEvicted` even documents this as loss: "lost_bytes is what the user paid for and won't get to use." This is a permanent freezing/loss of funds already paid to the protocol, and it can also be used to fully starve an app's bandwidth allowance, causing its ISMP dispatches to be rejected (`GateError::NoAllowance`), i.e., "a route unable to deliver messages" for that app.

### Likelihood Explanation
The cheapest tier ($50/100KB per the docs) means evicting one victim subscription costs the attacker one cheapest-tier purchase per victim entry sitting ahead of the eviction point — the attacker only needs to push the queue length past 1024 by repeat-buying the same cheapest tier for the targeted `(app_chain, app)`, which the docs themselves acknowledge as a "pathological repeat-buy" scenario but do not prevent. Anyone with funds for ~1024 minimum-tier purchases (a bounded, attacker-controlled cost) can execute this against any specific target app without any special privilege, matching a reachable "bandwidth purchaser" path. The 1024 cap and per-target FIFO queue are fixed and can be exhausted deterministically.

### Recommendation
Do not let an unprivileged purchase for one target displace another party's unexpired, unconsumed subscription. Options: (1) key/limit eviction candidates to only expired or same-purchaser subscriptions; (2) charge an eviction fee/refund the evicted purchaser's remaining pro-rated value from the evicting purchaser rather than silently dropping the entry; (3) raise or make the cap dynamic (e.g., per-payer sub-quota) so a single purchaser cannot flood another party's queue; or (4) reject a purchase that would evict a subscription with `remaining_bytes > 0` and `expires_at > now`, forcing the purchase to fail with `QueueFull` instead of silently destroying value.

### Proof of Concept
1. Victim's app has one active subscription at position 0 of its `(app_chain, app)` FIFO list with substantial `remaining_bytes` and a not-yet-expired `expires_at`.
2. Attacker (an "bandwidth purchaser," fully unprivileged) repeatedly calls `BandwidthManager.purchase()` targeting the *same* `app_chain`/`app` as the victim, each purchase dispatching a `BandwidthPurchaseMsg` that lands via `on_accept` and calls `push_subscription`.
3. Once 1024 such attacker purchases have landed, the next relayed purchase (the 1025th entry) causes `push_subscription` to call `list.remove(0)`, evicting the victim's still-live subscription and emitting `SubscriptionEvicted { lost_bytes: victim's remaining_bytes }`.
4. The victim's prepaid bytes are permanently lost — there is no on-chain refund; only a governance `force_credit` (admin-only) could restore the app, which is outside the victim's control. [4](#0-3)

### Citations

**File:** modules/pallets/bandwidth/src/lib.rs (L105-118)
```rust
	/// Keyed by `app_chain` from the purchase message — *not*
	/// `request.source` — so a payer chain can sponsor an app that
	/// lives elsewhere. The inner `BoundedVec` holds subscriptions in
	/// chronological insertion order; the gate drains the front.
	#[pallet::storage]
	pub type Allowance<T: Config> = StorageDoubleMap<
		_,
		Twox64Concat,
		StateMachine,
		Blake2_128Concat,
		AppKey,
		SubscriptionList,
		ValueQuery,
	>;
```

**File:** modules/pallets/bandwidth/src/lib.rs (L400-437)
```rust
		/// Append a fresh subscription with a fixed expiry. If the list
		/// is already at `MaxSubscriptions`, evict the oldest entry and
		/// emit [`Event::SubscriptionEvicted`] so the lost bytes are
		/// auditable. Returns the new subscription's `expires_at`.
		fn push_subscription(
			app_chain: &StateMachine,
			app: &AppKey,
			tier: TierIndex,
			bytes: BandwidthBytes,
			duration_secs: u64,
		) -> u64 {
			let now = <T as pallet_ismp::Config>::TimestampProvider::now().as_secs();
			let expires_at = now.saturating_add(duration_secs);
			let new_sub =
				Subscription { tier, remaining_bytes: bytes, expires_at, purchased_at: now };

			let evicted = Allowance::<T>::mutate(app_chain, app, |list| {
				let evicted = if list.len() == MAX_SUBSCRIPTIONS as usize {
					Some(list.remove(0))
				} else {
					None
				};
				// Capacity is now guaranteed; try_push can't fail.
				let _ = list.try_push(new_sub);
				evicted
			});

			if let Some(old) = evicted {
				Self::deposit_event(Event::SubscriptionEvicted {
					app_chain: *app_chain,
					app: app.clone(),
					tier: old.tier,
					lost_bytes: old.remaining_bytes,
				});
			}

			expires_at
		}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L439-445)
```rust
		/// The router uses this to skip the gate on purchases —
		/// otherwise a depleted app couldn't recharge.
		pub fn is_purchase_message(request: &PostRequest) -> bool {
			BandwidthManager::<T>::get(&request.source)
				.map(|m| request.from == m.0.to_vec())
				.unwrap_or(false)
		}
```
