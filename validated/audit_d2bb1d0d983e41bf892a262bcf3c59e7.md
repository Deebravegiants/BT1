### Title
Bandwidth subscription queue is a permissionless, purchase-priced DoS vector that permanently strands a legitimate app's prepaid bandwidth — ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth` stores a bounded FIFO queue of at most `MAX_SUBSCRIPTIONS` (1024) `Subscription` entries per `(app_chain, app)` key, exactly analogous to Salty.IO's capped `_openBallotsForTokenWhitelisting` queue. Any account able to trigger a `BandwidthManager.sol` purchase can push cheap, minimal-duration/minimal-byte subscriptions for a *specific target app* it does not own, and once the queue for that `(chain, app)` reaches 1024 entries, `push_subscription` silently evicts the oldest entry — including a legitimate, large, long-duration prepaid subscription a victim app already paid for — exactly as the report describes for the DAO whitelist queue filling up and blocking/erasing legitimate entries.

### Finding Description
`Allowance<T>` is a `StorageDoubleMap<StateMachine, AppKey, SubscriptionList>` where `SubscriptionList = BoundedVec<Subscription, ConstU32<1024>>` [1](#0-0) . Every accepted purchase message calls `push_subscription`, which is a pure FIFO append-with-eviction: once the list length equals `MAX_SUBSCRIPTIONS`, the oldest (index 0) subscription is unconditionally removed and the new one is appended [2](#0-1) .

Crucially, the `app` key on which `push_subscription` operates is **entirely attacker-chosen** and taken directly from the untrusted purchase message body decoded in `on_accept`:
```
let key = AppKey::truncate_from(msg.app);
let expires_at = Self::push_subscription(&msg.chain, &key, tier, bytes, duration);
``` [3](#0-2) 
Nothing ties the purchaser to the `app` being credited — the only requirement is that `request.from` matches the registered `BandwidthManager` for the source chain, which is satisfied by any caller of `BandwidthManager.sol`'s purchase entrypoint, not by the app owner. Any account with the (presumably small) fee for the cheapest tier can therefore target any victim `(chain, app)` pair and enqueue as many 1-month/cheapest-tier `Subscription` rows as it likes.

Because the queue caps at 1024 and evicts index 0 (the oldest, not the smallest or already-expired), an attacker who buys 1024 minimal-duration/minimal-byte subscriptions for a victim app's key will silently expel the victim's own real subscription(s) from the queue if the victim's subscription is older than the flood, or block-out room so that a future *legitimate* top-up purchase for that app immediately evicts the still-active, unconsumed victim entry once the 1024 cap is reached again. The eviction is unconditional on remaining balance — an entry with millions of `remaining_bytes` and years left before `expires_at` is evicted with the same priority as an empty, expired one, exactly like Salty's inability to distinguish or remove "spurious" proposals from legitimate ones except via a slow, potentially unincentivized process. Here there is no removal/curation mechanism at all — eviction is FIFO-blind.

The gate (`BandwidthGate::try_consume`) that ISMP-gates the app's real cross-chain messages consults exactly this list [4](#0-3) ; once the paid-for subscription is evicted, the app's dispatched messages start failing the gate (`GateError::NoAllowance` / `Insufficient`), even though the app already paid for and should still have bandwidth remaining.

### Impact Explanation
This is a permanent, protocol-level fund/service loss for the victim app: bandwidth that was paid for (real ETH/token fee via `BandwidthManager.sol`) is silently destroyed before being consumed, and the victim's ISMP messages are then rejected by the `BandwidthGate` hook for lack of allowance — a denial of service on the victim app's ability to use Hyperbridge messaging that it already paid for. Because `push_subscription` has no per-purchaser rate limit, minimum-value floor, or app-ownership check, and because eviction is oldest-first regardless of remaining value, a well-funded attacker (a competitor to the victim app, as in the original report's exploit scenario) can repeatedly and cheaply grief any specific app's prepaid allowance. This matches the report's "Medium" bug class of unbacked/permanent loss caused by a spam-fillable capped queue, escalated here because the loss is of already-paid, real value rather than merely blocking a governance proposal slot.

### Likelihood Explanation
The attack requires only funds to pay for 1024 cheapest-tier purchases (bounded, attacker-controlled cost) routed through the legitimate, permissionless `BandwidthManager.sol` → ISMP `on_accept` path; there is no admin/governance precondition, no need to compromise the victim, and no special privilege — matching the "external attacker with no privileged keys" baseline. The victim app has no way to protect its own prepaid subscription from eviction since the queue and eviction policy are entirely oldest-first and blind to remaining bytes/expiry distance. The comment in the module documentation itself ("Pushes onto a full list evict the oldest entry") shows this is a known, accepted design tradeoff rather than a bug that was hardened against adversarial `app`-key targeting, making exploitation straightforward once an attacker identifies a funded victim app.

### Recommendation
- Require the purchaser (via `request.from`/msg signer) to be the `app` being credited, or otherwise bind purchases to an authenticated owner of the `app` key, so unrelated third parties cannot push subscriptions onto a victim's queue.
- Change eviction policy so that entries with non-trivial `remaining_bytes` and/or a long time-to-expiry are not evicted ahead of near-empty/near-expired ones (e.g., evict expired entries first, or weight eviction by remaining value rather than pure FIFO position).
- Consider a minimum-value/minimum-duration floor per purchase and/or a per-purchaser rate limit on `push_subscription` for a given `(chain, app)`, mirroring the "larger deposit, refundable to legitimate proposer" mitigation recommended in the original report.
- Emit `SubscriptionEvicted` loudly enough (already done) but also expose a query/alert path so an app operator can detect an ongoing flood before their real allowance is destroyed, and consider adding admin tooling to clear or reorder a spammed queue (an authorized-removal mechanism, per the original report's short-term recommendation).

### Proof of Concept
1. Attacker identifies a victim app `V` on chain `C` that has purchased (or will purchase) a large, long-duration bandwidth subscription via `BandwidthManager.sol`, crediting `Allowance[C][V]`.
2. Attacker (any account, no relationship to `V` required) repeatedly calls the purchase entrypoint on the registered `BandwidthManager` contract for chain `C`, each time setting the purchase message's `app` field to `V`'s `AppKey` and choosing the cheapest tier/lowest duration.
3. Each purchase message is delivered via ISMP to `pallet-bandwidth::on_accept`, which decodes `msg.app == V` and calls `push_subscription(&C, &V, tier, bytes, duration)` [5](#0-4) .
4. Once `Allowance[C][V].len() == 1024`, each subsequent attacker purchase evicts index 0 of the FIFO list [6](#0-5) . Because insertion order (not remaining value) determines eviction order, the attacker can arrange (by pacing purchases before/after `V`'s legitimate purchase) for `V`'s real, high-value subscription to be the oldest entry and thus be evicted, destroying `V`'s paid bandwidth before it is consumed.
5. `V`'s subsequent cross-chain dispatches are rejected by `BandwidthGate::try_consume` with `GateError::NoAllowance`/`Insufficient`, even though `V` paid for bandwidth that should still be available — a concrete loss of paid-for service, achievable by any funded, unprivileged attacker.

### Citations

**File:** modules/pallets/bandwidth/src/lib.rs (L109-118)
```rust
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
