### Title
Sponsored bandwidth purchase griefing — attacker evicts a victim app's paid subscriptions via cheap 1-byte, 1-second purchases on any chain that sponsors that app - (File: modules/pallets/bandwidth/src/lib.rs)

### Summary
This is a direct structural analog of the VotingEscrow `MAX_DELEGATES` griefing report: both bugs are "cheap, unprivileged pushes into a bounded FIFO structure keyed by a victim identity, causing eviction/blocking of the victim's legitimately-earned entries."

### Finding Description
`pallet-bandwidth` stores prepaid bandwidth as a `BoundedVec<Subscription, MAX_SUBSCRIPTIONS>` (`MAX_SUBSCRIPTIONS = 1024`) inside `Allowance<T>`, keyed by `(app_chain, app)` — **not** keyed by the payer: [1](#0-0) [2](#0-1) 

The pallet's own doc comment explicitly states the design intent that lets this happen: "any deployment can sponsor any app on any chain," and a purchase's `app_chain`/`app` fields — freely chosen by the caller of `BandwidthManager.sol` on the source chain — determine which victim's row receives the new entry, independent of `request.source` (the payer chain): [3](#0-2) 

`push_subscription` is the append path used by every real purchase (`on_accept`) and by admin `force_credit`. When the target `(app_chain, app)` list is already at the 1024 cap, the **oldest** entry is evicted (FIFO), regardless of how much the evicted entry cost or how much bandwidth it still had left: [4](#0-3) 

`on_accept` decodes an inbound purchase message and calls `push_subscription` using the message's own `msg.chain` / `msg.app`, i.e., attacker-controlled destination fields, with `tier`/`months` also attacker-chosen (bounded only by whatever tiers are configured and priced on the EVM `BandwidthManager` side): [5](#0-4) 

Just as Bob in the VotingEscrow report created 1024 tiny locks and delegated each to Alex to fill `dstTokenIds` before Maya's legitimate delegation, an attacker here can send 1024 cheap purchase messages (minimum non-zero tier, 1 month) targeting a specific victim's `(app_chain, app)` key from any chain with a registered `BandwidthManager`. Each purchase appends one entry; the 1025th purchase — which could be the *victim's own real, large, paid-for renewal* — evicts the oldest entry in the queue. If the attacker keeps refilling the queue (repeating the cheap-purchase spam whenever it drains), the victim's genuine, larger subscriptions can be pushed out of the FIFO before being consumed by `try_consume`, and the victim is permanently deprived of the bandwidth it paid a real market price for.

### Impact Explanation
`BandwidthGate::try_consume` is the sole gate the ISMP router consults before accepting a message from a given app; running out of allowance (`GateError::NoAllowance`/`Insufficient`) causes legitimate cross-chain messages from that app to be rejected: [6](#0-5) 

An attacker who cheaply fills a victim's `Allowance` FIFO can (a) force eviction of the victim's real, paid bandwidth (`SubscriptionEvicted` — "what the user paid for and won't get to use"), directly causing financial loss to the sponsored app/user, and (b) degrade or fully block a route's ability to have its messages accepted by pallet-bandwidth's gate, i.e., "a route unable to deliver messages," matching the accepted impact classes for this scan. This is Medium/High severity: concrete, permanent loss of paid-for funds (bandwidth credits) and denial of message delivery for a targeted app, reachable purely from unprivileged, attacker-submitted purchase messages.

### Likelihood Explanation
Likelihood is High for any deployment where at least one tier is cheap (e.g., a low-cost/short-duration tier exists commercially) and `set_manager` has registered a `BandwidthManager` for at least one source chain, since:
- Any account can call the EVM `BandwidthManager.sol` purchase function specifying an arbitrary `app_chain`/`app` (the victim's), requiring only the tier's list price, which the attacker controls the minimality of by choosing the cheapest tier and 1 month.
- The pallet applies no restriction tying `app_chain`/`app` to the payer identity (this is a documented, intentional "sponsorship" feature), so nothing prevents targeting an arbitrary victim.
- The eviction is unconditional FIFO once the 1024 cap is hit — no anti-spam accounting, minimum-value protection, or per-payer quota exists in `push_subscription`.

The only mitigating factor is the need to reach 1024 entries per attack cycle, which costs `1024 × (cheapest tier price)`, similar in spirit to Bob's `0.0001024 ether` in the original report — cheap relative to fully bricking or repeatedly draining a targeted app's paid bandwidth.

### Recommendation
- Track and enforce fairness/eviction by payer or by minimum remaining value rather than pure insertion-order FIFO — e.g., never evict a subscription whose `remaining_bytes` exceeds some threshold, or evict the entry with the least remaining value first instead of strictly the oldest.
- Consider capping the number of subscriptions a single `(source_chain, payer)` pair may contribute per `(app_chain, app)` row, or requiring a minimum tier/duration threshold to be eligible to displace another payer's entry.
- Alternatively, key `Allowance` per `(app_chain, app, paid_from)` so one sponsor cannot evict another's credits, aggregating balances instead of a single shared insertion-ordered FIFO.
- Emit and monitor `SubscriptionEvicted` volume per `(app_chain, app)` to detect this pattern in production and consider automatically pausing further evictions once anomalous churn is observed.

### Proof of Concept
Conceptual reproduction (mirrors the VotingEscrow Foundry PoC structure), to be implemented against the pallet's test harness in `modules/pallets/bandwidth/`:
1. Admin calls `set_manager(source, manager)` and `set_tier(TierIndex::TierOne, Some(TierConfig { bytes: 1, duration_secs: 1 }))` (cheapest possible tier).
2. Victim's app (`app_chain = EVM(X)`, `app = victim_app_bytes`) has previously purchased a large, long-duration subscription via a legitimate `on_accept` purchase, landing at position 0 (oldest) — or any position — in `Allowance::<T>::get(app_chain, app)`.
3. Attacker crafts 1024 inbound purchase requests (simulating `BandwidthManager.sol` purchases) each with `msg.chain = app_chain`, `msg.app = victim_app_bytes`, `tier = TierOne`, `months = 1`, dispatched through `Pallet::<T>::on_accept`.
4. After the 1024th attacker purchase, `Allowance::<T>::get(app_chain, victim_app_bytes)` no longer contains the victim's real subscription — `push_subscription`'s `list.remove(0)` evicted it once the list reached `MAX_SUBSCRIPTIONS` — verified via the `Event::SubscriptionEvicted { app_chain, app, tier, lost_bytes }` event carrying the victim's original `tier`/`lost_bytes`.
5. `BandwidthGate::try_consume(app_chain, victim_app_bytes, N)` for a request needing more bytes than the attacker's residual cheap entries now returns `GateError::Insufficient`/`NoAllowance`, blocking the victim's legitimate cross-chain messages despite having paid for real bandwidth. [4](#0-3) [5](#0-4)

### Citations

**File:** modules/pallets/bandwidth/src/types.rs (L19-22)
```rust
/// Hard cap on the subscription list per `(chain, app)`. Pushes
/// beyond this evict the oldest entry (FIFO).
pub const MAX_SUBSCRIPTIONS: u32 = 1024;
pub type MaxSubscriptions = ConstU32<MAX_SUBSCRIPTIONS>;
```

**File:** modules/pallets/bandwidth/src/lib.rs (L16-33)
```rust
//! # pallet-bandwidth
//!
//! Prepaid `(chain, app)` byte balances credited by tier purchases
//! from `BandwidthManager.sol`. Each purchase carries its own
//! `app_chain`, so any deployment can sponsor any app on any chain.
//!
//! Each `(chain, app)` row holds a FIFO list of [`Subscription`]s
//! (`BoundedVec`, capped at 1024). Every purchase appends a new
//! subscription with a fixed `expires_at`; expiry never extends and
//! same-tier repurchases don't stack — they queue. The gate drains
//! the oldest live subscription first; once empty it moves to the
//! next. Subscriptions that aren't reached before their expiry are
//! swept silently — what you paid for is yours only until it expires.
//! Pushes onto a full list evict the oldest entry and emit
//! [`Event::SubscriptionEvicted`].
//!
//! [`BandwidthGate`] is the hook the runtime's ISMP router consults
//! for every message; insufficient balance → rejected.
```

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

**File:** modules/pallets/bandwidth/src/lib.rs (L466-486)
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
				paid_from: request.source,
				tier,
				bytes,
				expires_at,
			});
```

**File:** modules/pallets/bandwidth/src/lib.rs (L509-564)
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

			Ok(total)
		})?;

		Self::deposit_event(Event::BandwidthConsumed {
			source: *source,
			app: key,
			bytes: need,
			remaining: total - need,
		});
		Ok(())
	}
```
