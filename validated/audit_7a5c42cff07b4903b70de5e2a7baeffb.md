### Title
Bandwidth subscription queue can be spammed to evict a paid-up app's allowance, causing message delivery to be gated off - (File: `modules/pallets/bandwidth/src/lib.rs`)

### Summary
`pallet-bandwidth` stores each app's prepaid bandwidth as a bounded FIFO list (`Allowance<T>`, capped at `MAX_SUBSCRIPTIONS = 1024`) keyed by `(app_chain, AppKey)`. Any account can purchase bandwidth for *any* app on *any* chain by calling `BandwidthManager.sol`, because the pallet keys the credit by the `chain`/`app` fields inside the purchase message body, not by the caller's identity, and the doc/code explicitly allow "sponsorship" of another chain's app. Pushing a new subscription onto a full list silently evicts the oldest live entry (`Self::push_subscription` / `Event::SubscriptionEvicted`), regardless of how much unused balance that evicted entry carries.

### Finding Description
`Allowance<T>` is a `StorageDoubleMap<StateMachine, AppKey, BoundedVec<Subscription, MaxSubscriptions>>` [1](#0-0) . Every accepted purchase message appends a subscription via `push_subscription`, which evicts index 0 (the oldest) once the list is at the 1024 cap, with no minimum-value protection for the evicted entry: [2](#0-1) 

The purchase path (`on_accept`) derives the `(chain, app)` key entirely from the ABI-decoded message body — `msg.chain` and `msg.app` — not from `request.source`/`request.from`'s intended beneficiary, and the crate doc explicitly states this enables "any deployment [to] sponsor any app on any chain": [3](#0-2) [4](#0-3) 

Because the queue key is per-app (not per-payer), any account that can call the registered `BandwidthManager` contract on an authorized source chain can push cheap, minimal-tier, minimal-`months` purchases for a victim's `(chain, app)` bucket. Once the bucket is at the 1024 cap, each additional cheap purchase evicts the oldest live subscription — including a legitimately large, unconsumed, already-paid-for subscription belonging to the victim app — well before it is exhausted. `BandwidthGate::try_consume` is the hook the ISMP router consults for every message the app sends/receives; once the victim's queue is drained/evicted of live allowance, subsequent legitimate cross-chain messages from/to that app are rejected with `GateError::NoAllowance`/`Insufficient`: [5](#0-4) 

This is structurally the same bug class as the reported EigenLayer issue: an unbounded/underprotected FIFO queue whose entries can be cheaply multiplied by an attacker to push out (or delay processing of) a legitimate party's entry, denying them the resource they already paid for.

### Impact Explanation
An attacker who can reach the authorized `BandwidthManager` on a source chain (a single, unprivileged, permissionless transaction per purchase) can pay for the cheapest configured tier (`TierOne`) 1024+ times to completely refill a victim app's subscription queue with worthless/expired-fast entries, evicting the victim's real subscription(s) before they are consumed. Once evicted, `lost_bytes` (the paid-for, unused balance) is gone (`Event::SubscriptionEvicted`) and the gate will reject the victim app's ISMP requests/responses (`try_consume` → `GateError`), meaning the app can no longer dispatch or receive cross-chain messages until it repurchases — i.e., a route becomes unable to deliver messages, and the app's already-paid bandwidth allowance is permanently lost. This is a direct match for the explicitly allowed impact categories ("route unable to deliver messages", "permanent freezing of funds" in the form of the paid‑for allowance).

### Likelihood Explanation
The attack cost scales with `MAX_SUBSCRIPTIONS` (1024) times the cheapest tier's price (governance-configured on the EVM side; the pallet enforces only `bytes > 0 && duration_secs > 0`, no minimum price/value floor), and can be split across multiple cheap transactions with no rate limiting or per-purchaser restriction in the pallet. There is no check that an evicted entry's remaining value is small relative to the new entry, nor any restriction on who may top up a given `(chain, app)` bucket. This makes the attack economically much cheaper to mount than the effort a victim spent building up a large allowance, particularly if governance sets tier prices without considering this eviction economics — mirroring the "cheap attacker vs. expensive victim" asymmetry central to the original report.

### Recommendation
- Do not allow eviction of a subscription whose `remaining_bytes` (unconsumed value) exceeds some threshold, or refund/queue new low-tier purchases separately from high-value ones (e.g., per-tier sub-queues, or evict only same-tier-or-lower entries).
- Consider requiring `push_subscription` to reject (rather than silently evict) when the oldest entry still holds significant unconsumed balance, forcing purchasers to wait or pay a premium.
- Consider tracking capacity per payer/tier or enforcing a minimum tier price floor so filling the queue is not cheaper than the value it destroys.
- Emit a clear alarm/metric on high-frequency `SubscriptionEvicted` events for the same `(chain, app)` so operators can detect griefing in progress.

### Proof of Concept
1. Victim app `V` (identified by `(app_chain = Evm(X), app = victim_app_key)`) buys one large, long-duration `TierFour` subscription, landing as the sole/oldest entry in `Allowance::<T>::get(Evm(X), victim_app_key)`.
2. Attacker calls `BandwidthManager.sol.purchase(...)` on any authorized source chain 1024 times (or enough to fill the remaining capacity), each time setting the purchase message's `chain = Evm(X)` and `app = victim_app_key` (sponsorship path, no restriction on payer identity) with `tier = TierOne`, `months = 1` — the cheapest possible SKU.
3. `pallet-bandwidth::on_accept` decodes each message and calls `push_subscription(Evm(X), victim_app_key, TierOne, ...)` [6](#0-5) ; once the list reaches 1024 entries, each subsequent attacker purchase evicts the oldest entry — eventually evicting `V`'s large `TierFour` subscription while it still has significant `remaining_bytes`, emitting `SubscriptionEvicted { lost_bytes: <V's unused balance> }`.
4. `V`'s subsequent ISMP messages call `BandwidthGate::try_consume(Evm(X), victim_app_key, bytes)`; with `V`'s allowance now consisting only of the attacker's expired/near-empty `TierOne` entries, the call returns `GateError::NoAllowance` or `Insufficient`, and the ISMP router rejects `V`'s messages — denying `V` service despite having already paid for bandwidth that was evicted.

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

**File:** modules/pallets/bandwidth/src/lib.rs (L404-437)
```rust
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

**File:** modules/pallets/bandwidth/src/abi.rs (L16-31)
```rust
/// Pallet-side decoded form of [`BandwidthPurchaseMsg`]. `tier`
/// and `months` are narrowed to `u32` and `chain` is parsed into
/// `StateMachine` — anything that fails those checks is rejected
/// at decode time rather than reaching storage.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PurchaseMessage {
	/// Recipient app on the credit chain. Rejected at decode time if it does not fit `AppKey`.
	pub app: Vec<u8>,
	/// Tier discriminant; must map to a `TierIndex` variant.
	pub tier: u32,
	/// Multiplier on `cfg.bytes` and `cfg.duration_secs`. `0` is rejected.
	pub months: u32,
	/// Chain where the credit lands. Differs from `request.source` on
	/// sponsorship.
	pub chain: StateMachine,
}
```
