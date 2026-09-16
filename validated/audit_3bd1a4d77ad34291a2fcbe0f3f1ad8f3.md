## Analysis

The strongest analog to the Y2K `mintDepositInQueue` DOS is `pallet-bandwidth`'s per-`(chain, app)` FIFO subscription list, which is grown and drained via a purely permissionless dispatch path.

### Title
Unprivileged repeated `purchase()` on `pallet-bandwidth` evicts and permanently destroys another payer's unconsumed bandwidth subscription - (File: `modules/pallets/bandwidth/src/lib.rs`)

### Summary
`pallet-bandwidth`'s `Allowance` storage is a `BoundedVec<Subscription, 1024>` FIFO keyed by `(app_chain, app)`, appended to on every accepted purchase message and drained oldest-first by the gate. When the list is full, `push_subscription` unconditionally evicts (deletes) the oldest live entry to make room for the new one [1](#0-0) . Because any address can call `purchase()` on `BandwidthManager.sol` for *any* `app`/`app_chain` pair — the `chain` field in the purchase message is attacker-controlled and independent of `request.source` — an attacker (who does not need to be the app owner) can spam 1024 minimal purchases targeting a victim app's `(app_chain, app)` key to push the victim's still-unconsumed, previously-paid-for subscription out of the FIFO before it is drained by the gate.

### Finding Description
- `Allowance` is a `StorageDoubleMap` of `(StateMachine, AppKey) -> SubscriptionList` where `SubscriptionList = BoundedVec<Subscription, MaxSubscriptions>` (`MAX_SUBSCRIPTIONS = 1024`) [2](#0-1) .
- `on_accept` is reached by any inbound ISMP POST from a registered `BandwidthManager` contract; the only sender check is that `request.from` equals the registered manager address for `request.source` — this does not restrict which `(chain, app)` bucket the purchase targets, since `msg.chain` and `msg.app` are attacker-supplied fields of the ABI-decoded purchase body [3](#0-2) .
- `push_subscription` is the FIFO insertion point: once `list.len() == MAX_SUBSCRIPTIONS`, it removes index `0` (the oldest entry, which is exactly the drain order the gate consumes) and appends the new entry [1](#0-0) .
- The gate (`BandwidthGate::try_consume`) always drains from the front (oldest) of the list [4](#0-3)  — the same FIFO-drain / FIFO-evict design the Y2K report calls out as *not* vulnerable to this class of attack (in Y2K, the fix suggested moving from LIFO to FIFO precisely to prevent early depositors from being starved). Here, the structure is already FIFO for drain, but the *eviction* on overflow removes the oldest live (paid-for, unconsumed) entry rather than rejecting the new purchase or evicting the newest, which reintroduces the same "first-in, permanently-starved" outcome the FIFO drain was meant to avoid.
- This directly loses real value: `Event::SubscriptionEvicted` documents `lost_bytes` — bytes the original payer purchased and paid the manager's fee-token price for but never got to consume [5](#0-4) [6](#0-5) . There is no way for the evicted party to reclaim it.

### Impact Explanation
An attacker can permanently destroy a legitimate app's already-paid-for bandwidth allowance by targeting its `(app_chain, app)` bucket with enough cheap purchases to push the cap and evict the victim's entry before the gate drains it. This is a concrete, unrecoverable loss of funds (the fee token paid for the tier is non-refundable once evicted) for any app that purchases bandwidth, and it can be repeated indefinitely against any app, effectively acting as permanent value destruction / theft of the economic value of a subscription that was never actually consumed. Because purchase targeting is keyed purely by attacker-supplied `msg.chain`/`msg.app` fields rather than by the manager's own source chain, the blast radius covers every `(chain, app)` pair on the protocol, not just pairs the attacker directly transacts through.

### Likelihood Explanation
Reaching this path requires only: (1) calling `purchase()` on any registered `BandwidthManager` contract — a fully permissionless, unprivileged entry point available to anyone with fee-token balance, and (2) doing so 1024 times against the same target `(app_chain, app)`. There is no per-caller rate limiting, no minimum purchase interval, and no protection preventing a purchase targeting an arbitrary `(chain, app)` pair not related to the caller's own chain. The only friction is the cumulative tier price for 1024 purchases, which is a real but bounded, attacker-controllable cost (paid once per purchase, at the cheapest configured tier) — this makes the attack a paid griefing vector rather than a free one, but it remains fully executable by a single unprivileged actor with no special access, and it scales linearly (not exponentially) with the number of entries to evict.

### Recommendation
- Reject (rather than silently evict) a purchase that would overflow the FIFO cap for an app that still has unexpired subscriptions, or route the credit to top up/merge into an existing untouched entry instead of always appending a new row.
- Alternatively, key eviction eligibility on subscription *age relative to expiry* rather than strict insertion order, or add a cool-down / minimum-remaining-bytes threshold under which eviction is disallowed for a not-yet-consumed subscription.
- Consider capping the number of subscriptions a single purchase can add per unit time per `(chain, app)`, or requiring that only the registered manager's own bound chain (i.e., `request.source == msg.chain`) may credit a bucket, removing the ability for arbitrary third-party managers/chains to target any victim app.

### Proof of Concept
1. Governance registers `BandwidthManager` for `source = EVM-1` and configures `TierOne` with `bytes = X`, `duration_secs = D` on both sides.
2. Victim app `A` on `app_chain = EVM-8453` legitimately buys `TierOne` bandwidth via `purchase()`, dispatching a `BandwidthPurchaseMsg{ app: A, tier: TierOne, months: 1, chain: EVM-8453 }`; `on_accept` appends this subscription at index 0 of `Allowance[(EVM-8453, A)]` [7](#0-6) .
3. Attacker, from the same or any registered manager chain, repeatedly calls `purchase()` 1024 times, each time encoding `chain = EVM-8453` and `app = A` (the victim's key) in the purchase body — a value the pallet trusts unconditionally from the decoded message body, with no check tying it to `request.source` or `request.from` beyond manager identity [8](#0-7) .
4. On the 1024th attacker purchase, `push_subscription` detects `list.len() == MAX_SUBSCRIPTIONS` and evicts index 0 — the victim's still-unconsumed original subscription — emitting `SubscriptionEvicted{ app_chain: EVM-8453, app: A, lost_bytes: X }` [9](#0-8) .
5. The victim's paid-for bandwidth (`X` bytes) is now permanently gone; any messages the victim app dispatches through the gate are rejected with `NoAllowance`/`Insufficient` despite having paid for allowance that was never consumed.

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

**File:** modules/pallets/bandwidth/src/lib.rs (L167-175)
```rust
		},
		/// The 1024-cap pushed out the oldest subscription. `lost_bytes`
		/// is what the user paid for and won't get to use.
		SubscriptionEvicted {
			app_chain: StateMachine,
			app: AppKey,
			tier: TierIndex,
			lost_bytes: BandwidthBytes,
		},
```

**File:** modules/pallets/bandwidth/src/lib.rs (L416-434)
```rust
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
```

**File:** modules/pallets/bandwidth/src/lib.rs (L441-445)
```rust
		pub fn is_purchase_message(request: &PostRequest) -> bool {
			BandwidthManager::<T>::get(&request.source)
				.map(|m| request.from == m.0.to_vec())
				.unwrap_or(false)
		}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L454-489)
```rust
	impl<T: Config> IsmpModule for Pallet<T> {
		fn on_accept(&self, request: PostRequest) -> Result<Weight, anyhow::Error> {
			let manager = BandwidthManager::<T>::get(&request.source).ok_or_else(|| {
				anyhow::anyhow!(format!("no bandwidth manager registered for {:?}", request.source))
			})?;

			if request.from != manager.0.to_vec() {
				return Err(anyhow::anyhow!(format!(
					"purchase from unauthorised sender on {:?}: expected {:x?}, got {:x?}",
					request.source, manager.0, request.from
				)));
			}

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
				paid_from: request.source,
				tier,
				bytes,
				expires_at,
			});

			Ok(Weight::zero())
		}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L536-552)
```rust
			// Drain from the front in insertion order. Once a sub is
			// fully consumed, pop it and continue with the next.
			// `get_mut` defends against a malformed list that satisfies
			// the `total >= need` precheck but is structurally empty;
			// we'd otherwise panic via `list[0]`.
			let mut left = need;
			while left > 0 {
				let Some(head) = list.get_mut(0) else {
					return Err(GateError::NoAllowance);
				};
				let take = head.remaining_bytes.min(left);
				head.remaining_bytes = head.remaining_bytes.saturating_sub(take);
				left = left.saturating_sub(take);
				if head.remaining_bytes == 0 {
					list.remove(0);
				}
			}
```

**File:** modules/pallets/bandwidth/src/types.rs (L95-111)
```rust
/// drains via the gate, `expires_at` is fixed at purchase time and
/// never extends. Repurchases append a new row instead of stacking.
#[derive(
	Encode, Decode, DecodeWithMemTracking, TypeInfo, MaxEncodedLen, Clone, PartialEq, Eq, Debug,
)]
pub struct Subscription {
	/// SKU this subscription was bought against; for analytics/events
	/// only — the gate doesn't look at it during drain.
	pub tier: TierIndex,
	/// Bytes left to spend. Decrements as the gate drains; the entry
	/// is popped once this hits zero.
	pub remaining_bytes: BandwidthBytes,
	/// Unix seconds. Gate sweeps entries where `expires_at <= now`.
	pub expires_at: u64,
	/// Unix seconds at insertion — fixes FIFO order under same-block buys.
	pub purchased_at: u64,
}
```
