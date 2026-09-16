### Title
Unbounded per-purchase subscription list in `pallet-bandwidth`'s `try_consume` can be inflated by many small buys, making bandwidth-gated message delivery expensive or blocked - (File: modules/pallets/bandwidth/src/lib.rs, modules/pallets/bandwidth/src/types.rs)

### Summary
`BandwidthGate::try_consume` (called on every non-purchase inbound POST request from a bandwidth-managed source chain) sweeps and drains a FIFO `BoundedVec<Subscription, ConstU32<1024>>` list that grows with every purchase. Analogous to the `ProtectionPool._accruePremiumAndExpireProtections()` report — an unbounded, state-size-dependent loop reachable by ordinary usage — repeated small purchases against a single `(chain, app)` key can grow the subscription list to its 1024-entry cap, after which every subsequent message dispatch for that app must iterate/sweep the full list inside `try_consume`, with cost charged against a static, size-independent weight.

### Finding Description
`try_consume` in `modules/pallets/bandwidth/src/lib.rs` performs, on every call:
1. `list.retain(|s| s.expires_at > now)` — an O(n) sweep over the entire subscription list.
2. A `while left > 0 { ... }` drain loop that walks the list from the head until the requested bytes are satisfied. [1](#0-0) 

The list is a `BoundedVec` capped at `MAX_SUBSCRIPTIONS = 1024` [2](#0-1) , and `push_subscription` appends one new entry per purchase, evicting only the oldest entry once the cap is reached [3](#0-2) . Nothing prevents an app (or anyone funding purchases for that `(app_chain, app)` key, since sponsorship is chain-agnostic per the docs) from repeatedly buying the smallest tier to push the list to its 1024-entry cap.

Crucially, `try_consume` is invoked from the ISMP router's `on_accept`/`on_response` path for *every* non-purchase message from that source/app pair [4](#0-3) , and the pallet's message-handling weight is a static constant unrelated to the actual list size being processed: `fn weight() -> Weight { Weight::from_parts(300_000_000, 0) }` in `pallet-ismp` (used as the default before `FeeHandler`/weight overrides) [5](#0-4) . This mirrors the original bug's core problem: a loop bound is dictated by accumulated on-chain state (all active protections / all subscriptions) rather than by the caller, so a single message's processing cost balloons with unrelated prior activity and is not reflected in the resources charged for it.

### Impact Explanation
If the subscription list for a given `(app_chain, app)` reaches the 1024-entry cap (e.g., via minimum-tier repeat purchases), every subsequent message delivery for that app must run the `retain` sweep and the FIFO drain loop across up to 1024 entries inside `try_consume`. Because this cost is not reflected in the extrinsic's declared weight, blocks containing such calls can under-account real execution time relative to the declared weight, which is a route-availability risk: worst-case per-message processing cost grows with unrelated purchase history, and repeated invocation against many bloated `(chain, app)` keys in one block can push actual execution time past the weight budget assumed by block production, threatening the timely inclusion/finalization of ISMP message-handling extrinsics for that app (and, if severe, for the block). This satisfies the "route unable to deliver messages" bar for a valid finding, though the concrete blast radius is bounded per-app (the cap is 1024 and per `(chain, app)` key, not global), which lowers severity relative to the original unbounded-across-entire-pool case.

### Likelihood Explanation
Reaching the cap requires an attacker (or misconfigured integrator) to make ~1024 minimum-tier purchases against a single `(app_chain, app)` pair, which costs real fee-token payment per purchase but is otherwise permissionless — anyone can call `BandwidthManager.purchase()` on the source chain to credit any `app` on any `app_chain` (per the sponsorship model). The cost of executing 1024-entry sweeps/drains per message, while not free, is not gated by anything beyond that one-time purchase cost, and it is *paid once* by the attacker but *imposed on every future deliverer* of a message to that app. Likelihood is Medium: it requires deliberate and sustained purchase spam (not merely "many buys" as an organic user pattern), and the impact is scoped to messages destined for the targeted app rather than protocol-wide.

### Recommendation
- Charge weight/fees for `on_accept`/`try_consume` proportional to `Allowance::<T>::decode_len()` (or track list length in a companion counter) rather than a static constant, so the true cost of a large subscription list is reflected in block weight accounting.
- Consider bounding per-call sweep/drain work (e.g., cap the number of subscriptions inspected per call, deferring further sweeping to a maintenance extrinsic or scheduled task) so a single message's processing time is independent of historical purchase count.
- Alternatively, coalesce same-tier repurchases into a single subscription (extend `remaining_bytes`/`expires_at`) instead of always appending a new FIFO entry, reducing the practical list length under repeat-buy behavior.

### Proof of Concept
1. Attacker (or anyone) registers/uses an existing `BandwidthManager` on a managed source chain and repeatedly calls `purchase()` for the smallest configured tier against a target `(app_chain, app)` pair, driving `Allowance::<T>` for that key from 0 to `MAX_SUBSCRIPTIONS` (1024) entries — each purchase appends via `push_subscription` [6](#0-5) .
2. Any subsequent legitimate message dispatched to that `app` from that `source` triggers `ProxyModule::on_accept` → `BandwidthGate::try_consume` [4](#0-3) .
3. `try_consume` executes `list.retain(...)` over up to 1024 entries and then the `while left > 0` drain loop, walking through however many entries are needed to satisfy the requested bytes [1](#0-0) , while the extrinsic is weighted as if this were O(1) work per the pallet's static weight function [5](#0-4) .
4. Repeating step 2 for many messages targeting the bloated app (or several such apps in the same block) accumulates real, unaccounted-for execution cost, risking delayed processing of ISMP messages for that app.

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

**File:** modules/pallets/bandwidth/src/lib.rs (L523-555)
```rust
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
```

**File:** modules/pallets/bandwidth/src/types.rs (L19-22)
```rust
/// Hard cap on the subscription list per `(chain, app)`. Pushes
/// beyond this evict the oldest entry (FIFO).
pub const MAX_SUBSCRIPTIONS: u32 = 1024;
pub type MaxSubscriptions = ConstU32<MAX_SUBSCRIPTIONS>;
```

**File:** parachain/runtimes/nexus/src/ismp.rs (L375-391)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L727-730)
```rust
	/// Static weights because these should get overridden by the FeeHandler
	fn weight() -> Weight {
		Weight::from_parts(300_000_000, 0)
	}
```
