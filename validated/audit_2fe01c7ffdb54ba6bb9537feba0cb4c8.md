### Title
`pallet-bandwidth`: sponsorship-keyed FIFO subscription list lets any purchaser grief-fill an app's `Allowance` bucket via cheap purchases — ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth`'s `Allowance` storage is a per-`(app_chain, app)` FIFO `BoundedVec<Subscription, 1024>` that any authorized `BandwidthManager` purchase message can append to, on behalf of an arbitrary target app, from any payer. Once the bounded list is full, further purchases silently evict the oldest live (unconsumed) subscription rather than reverting, exactly the griefing pattern in the reported Fenwick-tree bug: an unprivileged caller repeatedly "deposits" into another party's slot until the structure is full/rotated, destroying value that belonged to someone else.

### Finding Description
`Allowance` is keyed by `(app_chain, AppKey)` and explicitly **not** by payer: [1](#0-0) 

Any inbound `PurchaseMessage` from the registered `BandwidthManager` on a given source chain is accepted and pushed into the target `(msg.chain, msg.app)` bucket via `on_accept` → `push_subscription`, with no check that the caller/payer is related to the app being credited — sponsorship is a documented, intended feature ("a payer chain can sponsor an app that lives elsewhere"): [2](#0-1) 

`push_subscription` enforces the 1024-entry cap by **evicting the oldest entry** rather than rejecting the purchase: [3](#0-2) 

This is structurally the same class of bug as the reported `_registerKey`/`maxDepositEntries` issue: a bounded, shared-capacity data structure per beneficiary that anyone can push into (there, `addLiquidity` on behalf of another user; here, a purchase message crediting an arbitrary `app_chain`/`app` pair), where reaching the cap either blocks new legitimate entries (`Fenwicks_TooManyKeys`) or — worse here — silently destroys an existing legitimate entry's unconsumed value (`SubscriptionEvicted`).

Because `TierConfig.bytes`/`duration_secs` are admin-configured per tier and cheap low tiers can exist, an attacker who can reach the registered `BandwidthManager` on any authorized source chain (a normal, permissionless dApp call from `BandwidthManager.sol`, since anyone can call the EVM contract to buy bandwidth for any `app`/`chain` pair per the pallet's own doc comment) can issue 1024+ minimal purchases targeting a victim `(app_chain, app)` pair. Each purchase after the 1024th evicts and permanently destroys the oldest live subscription — including large, recently and legitimately purchased subscriptions belonging to the victim app — while the attacker pays only the cheapest tier's price for each entry.

Unlike the source report's tree (which only *blocks* future deposits, recoverable by withdrawal), this pallet's eviction is **destructive**: `lost_bytes` are gone forever with no refund path (`SubscriptionEvicted` is only an audit event, not a compensation mechanism), and there is no way for the victim app to reclaim or prevent this — the FIFO is drained in insertion order, oldest first, regardless of size, so a single attacker can force out a large legitimate multi-month purchase using many small cheap purchases.

### Impact Explanation
This is a permanent, unrecoverable loss of prepaid bandwidth for any app targeted by the attack: an attacker can force-expire (evict) a victim app's paid bandwidth allowance before it is consumed, causing the `BandwidthGate::try_consume` check used by the ISMP router to reject legitimate cross-chain messages for that app (`GateError::NoAllowance`/`Insufficient`) even though the app paid for bandwidth. This can be used to deny service to a target application indefinitely at low, repeatable cost to the attacker (bounded only by the cheapest configured tier price × 1024), which maps to concrete freezing of paid-for value and denial of the message-routing service the pallet gates.

### Likelihood Explanation
Medium-High: `set_manager`/tier configuration is admin-only, but issuing purchase messages through the authorized `BandwidthManager` contract for an arbitrary `app`/`app_chain` is, by the pallet's own design comment, an intentionally permissionless "sponsorship" feature ("any deployment can sponsor any app on any chain"). No signer/ownership check ties a purchase to the app it credits. The only cost to the attacker is paying for ~1024 cheap-tier purchases, which is a bounded, one-time cost to permanently evict a victim's allowance and can be repeated whenever the victim repurchases.

### Recommendation
- Do not silently evict live, unconsumed subscriptions to make room for new ones. Either reject the purchase (mirroring `Fenwicks_TooManyKeys`) once the list is full of *live* entries, or evict only fully expired/zero-`remaining_bytes` entries.
- Consider gating sponsorship: require the purchaser to be the app owner, an allowlisted sponsor, or otherwise rate-limit/aggregate low-value purchases per `(app_chain, app)` so a flood of minimal purchases cannot displace a large legitimate one.
- If FIFO eviction of live entries must remain for capacity reasons, evict by remaining value/size heuristics rather than strict insertion order, or increase/parametrize `MAX_SUBSCRIPTIONS` and add a governance-adjustable minimum bytes-per-purchase to make griefing economically infeasible.

### Proof of Concept
1. Admin registers a `BandwidthManager` for source chain `S` and configures `TierIndex::TierOne` with minimal `bytes`/`duration_secs` (`set_tier`).
2. Victim purchases a large, expensive tier subscription for `(app_chain = X, app = victimApp)` — this becomes entry 0 (oldest) in `Allowance::<T>::get(X, victimApp)`.
3. Attacker, using the same authorized `BandwidthManager` on `S` (any caller can invoke the deployed EVM `BandwidthManager` contract to buy the cheapest tier targeting `chain = X, app = victimApp`), submits 1024 minimal `TierOne` purchases.
4. Each `on_accept` call runs `push_subscription`; once the list reaches `MAX_SUBSCRIPTIONS = 1024`, subsequent pushes call `list.remove(0)`, evicting oldest-first — after enough purchases the victim's large subscription (entry 0) is evicted and `Event::SubscriptionEvicted` fires with the victim's `lost_bytes`.
5. Victim's app subsequently fails `BandwidthGate::try_consume` (`GateError::NoAllowance`/`Insufficient`) despite having paid, and the ISMP router rejects its messages — confirmed by the eviction/consume logic at: [4](#0-3) [5](#0-4)

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
