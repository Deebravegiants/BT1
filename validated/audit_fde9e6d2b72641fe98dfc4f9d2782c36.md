### Title
Bandwidth subscription FIFO cap can be gamed to evict a victim app's paid-for allowance - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth` caps each `(app_chain, app)` subscription list at `MAX_SUBSCRIPTIONS` (1024) and evicts the oldest entry on overflow. Any unprivileged caller can pay for cheap, low-value tier purchases targeting a victim's `(chain, app)` key to fill the FIFO list and force-evict the victim's legitimately purchased, larger/still-unconsumed subscription — permanently destroying bandwidth the victim already paid for. This mirrors the `maxRecordsPerTransaction` bug class: a protection mechanism (the 1024-entry cap, meant to bound storage) gives a false sense of safety while being trivially gameable by anyone willing to submit enough cheap transactions.

### Finding Description
`push_subscription` appends every purchase (via `BandwidthManager.purchase()` → ISMP POST → `on_accept`) to the `Allowance<T>` FIFO list keyed by `(app_chain, app)`, taken directly from the attacker-controlled purchase message body — not from `request.source`, which is exactly what makes cross-chain "sponsorship" possible but also what lets *anyone* target *any* app's allowance bucket: [1](#0-0) 

The eviction logic removes the oldest (`list.remove(0)`) entry once the list is at `MAX_SUBSCRIPTIONS`, regardless of who purchased it or how much unconsumed `remaining_bytes` it still holds: [2](#0-1) 

Because `Allowance` is keyed by `app_chain`/`app` from the message body rather than by payer, and any registered `BandwidthManager` will forward *any* caller's `purchase()` call, an attacker can:
1. Identify a victim app's `(app_chain, app)` key (public via `BandwidthCredited`/`BandwidthConsumed` events or `Pallet::allowances`).
2. Buy the cheapest configured tier (`TierOne`) 1024 times in quick succession (or fewer times if the victim's queue already has entries), each purchase appending a new subscription to the same `(app_chain, app)` bucket the victim uses.
3. Once the list is full, every subsequent cheap purchase evicts the oldest entry — which, once the attacker's spam has pushed past the victim's insertion point, is the victim's paid-for subscription, with `SubscriptionEvicted` firing and `lost_bytes` permanently gone.

This is structurally identical to the reported `maxRecordsPerTransaction` issue: the pallet enforces an on-chain invariant (a cap meant to keep the FIFO list bounded) that looks like protection but provides none against a determined single actor who is willing to pay the (governance-set, potentially low) tier price repeatedly. Unlike an NFT mint limited by wallet count, there isn't even a need for many wallets here — one account can submit 1024 sequential cheap purchases from a single address, since nothing rate-limits or per-account-limits purchases into another app's bucket.

### Impact Explanation
Medium: the victim application permanently loses bandwidth it already paid real fee-token value for (`SubscriptionEvicted { lost_bytes }`), and depending on timing can be pushed into `GateError::NoAllowance`, causing its subsequent legitimate ISMP dispatches to be rejected until it repurchases. This is a real, permanent loss of funds/service the victim paid for, and it can be triggered by a comparatively small amount of the cheapest tier, since the pallet does not weight eviction priority by size, tier, or payer.

### Likelihood Explanation
Medium: any address that knows a target's `(app_chain, app)` (which is emitted publicly in `BandwidthCredited`/`BandwidthConsumed` events) can carry out the attack purely with its own funds and without needing governance, admin, or victim cooperation — the same "cheap and easy, and we've seen it before" profile that made the reference report's minting-sniping scenario a documented risk.

### Recommendation
Do not let an eviction destroy unconsumed, still-live allowance purchased by a different payer than the one triggering the push. Options:
- Track `remaining_bytes` at eviction time and refuse (or refund) evicting a subscription that still has meaningful bytes left, or raise the cap / make it governance-configurable per app.
- Weight or prioritize eviction by remaining value (e.g., evict smallest/expired-soonest first) rather than strict FIFO regardless of size.
- Document explicitly (as the source report recommends for `maxRecordsPerTransaction`) that the 1024-cap is a storage-bound safety valve, not a griefing protection, and that apps should monitor `SubscriptionEvicted` and keep their queue depth low by consolidating purchases into larger tiers.

### Proof of Concept
1. Governance configures `TierOne` with a small `(bytes, duration_secs)` and a low fee-token price via `set_tier`/`dispatch_set_tiers`.
2. Victim app buys a large multi-month `TierFour` subscription for `(app_chain=Evm(8453), app=<victim>)`; `Allowance` list now holds 1 entry.
3. Attacker, from a single address, calls `BandwidthManager.purchase()` 1024 times with `app = <victim>`, `chain = "EVM-8453"`, `tier = TierOne`, `months = 1`, paying the cheap `TierOne` price each time.
4. Each purchase dispatches a `BandwidthPurchaseMsg` that lands on `on_accept`, calling `push_subscription`, which appends to the same `(Evm(8453), victim)` bucket the victim's subscription lives in — see `modules/pallets/bandwidth/src/lib.rs:400-437`.
5. On the purchase that brings the list to 1025 entries, `list.remove(0)` evicts whatever sits at the front. Once enough spam purchases have pushed past the victim's original insertion index (which happens once the attacker has bought slightly more than 1024 - (victim's original position) times), the victim's `TierFour` subscription — regardless of its large `remaining_bytes` — is evicted and `SubscriptionEvicted { lost_bytes: <victim's remaining> }` fires, permanently destroying bandwidth the victim paid for.

### Citations

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

**File:** modules/pallets/bandwidth/src/types.rs (L19-22)
```rust
/// Hard cap on the subscription list per `(chain, app)`. Pushes
/// beyond this evict the oldest entry (FIFO).
pub const MAX_SUBSCRIPTIONS: u32 = 1024;
pub type MaxSubscriptions = ConstU32<MAX_SUBSCRIPTIONS>;
```
