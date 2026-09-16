I have enough detail now to write the final analog finding.

### Title
Permissionless bandwidth purchases let anyone evict any app's paid subscriptions via the FIFO cap - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`BandwidthManager.purchase()` on any EVM source chain is fully permissionless: the caller freely chooses the `app` (recipient app identifier on the *credit* chain) and `chain` (credit chain) parameters, with no whitelist or ownership check tying the purchase to the app it credits. On Hyperbridge, `pallet-bandwidth::on_accept` (`modules/pallets/bandwidth/src/lib.rs:454-489`) only validates that the message came from the registered manager for the source chain — it never validates that the caller has any relationship to the `app` being credited. Every purchase calls `push_subscription`, which appends to a `BoundedVec` capped at `MAX_SUBSCRIPTIONS` (1024) per `(app_chain, app)`, silently evicting the oldest entry once full (`modules/pallets/bandwidth/src/lib.rs:400-437`).

### Finding Description
This mirrors the reported bug class ("a single account can create as many as possible" via an under-restricted creation path) but reachable by any unprivileged EVM caller rather than a governance-whitelisted address. Because:
1. `purchase()` takes `app` and `chain` as arbitrary caller-supplied bytes (`evm/src/apps/BandwidthManager.sol:153-200`), anyone can target *any other app's* `(chain, app)` allowance bucket.
2. `pallet-bandwidth::on_accept` only checks `request.from == registered manager` (`modules/pallets/bandwidth/src/lib.rs:460-465`); it does not check that the purchaser is the app itself or an authorized sponsor of it — this is by design for the "Sponsorship" feature (paying for another app's bandwidth from any chain).
3. `push_subscription` unconditionally evicts index 0 (the oldest, not necessarily the smallest or already-drained) once the FIFO list hits 1024 entries, regardless of how much of that entry's `remaining_bytes` is unused (`modules/pallets/bandwidth/src/lib.rs:416-425`).

An attacker can therefore repeatedly call `purchase()` (cheapest configured tier, `months = 1`) targeting a victim `(chain, app)` pair to push 1024 low-value junk subscriptions into that app's list, evicting the victim's legitimately purchased, still-unconsumed, higher-value subscriptions from the head of the queue.

### Impact Explanation
Each eviction permanently destroys `remaining_bytes` of prepaid bandwidth the legitimate purchaser already paid for — the pallet emits `SubscriptionEvicted { lost_bytes, ... }` precisely because "what you paid for is yours only until it expires" no longer holds once forcibly evicted early. This is a durable loss of funds paid in the fee token for a service (bandwidth allowance) that becomes permanently unusable, i.e., the app is bricked with respect to sending ISMP messages until it repurchases, while the attacker's cost only needs to cover 1024 minimum-tier purchases (the cheapest tier is fixed by governance and can be arbitrarily small in `bytes`/`duration_secs`, decoupled from the victim's purchased tier size). Any Hyperbridge app relying on paid bandwidth (rather than the governance `Allowlist` bypass) is exposed.

### Likelihood Explanation
`purchase()` requires no permission, allowlist membership, or relationship to the target app — it is callable by anyone holding fee tokens on any EVM chain with a registered `BandwidthManager`. The `app`/`chain` targeting is entirely attacker-controlled calldata. The only cost is the price of `1024` minimum-tier purchases, which is bounded and known once tier pricing is public, making this a deterministic, executable griefing/fund-loss vector rather than a probabilistic one.

### Recommendation
Do not use a single global 1024-cap FIFO keyed purely by `(app_chain, app)` that is populated by arbitrary third parties. Options: (1) require the purchase's originating manager/caller to be the app itself, or maintain a separate, larger/segregated allowance per payer so third-party sponsorship purchases cannot evict self-purchased entries; (2) evict expired-or-nearly-drained entries preferentially instead of strict oldest-first FIFO; (3) raise or make the cap governance-configurable per app based on purchase history/value so an attacker cannot cheaply fill it with dust-tier purchases; (4) rate-limit/cost-scale cross-app sponsorship purchases distinctly from self-purchases.

### Proof of Concept
1. Governance registers `BandwidthManager` for chain X and configures `TierOne` with minimal `(bytes, duration_secs)` and a low price (`set_manager`, `set_tier` in `modules/pallets/bandwidth/src/lib.rs:212-291`).
2. Victim app `A` on chain Y calls `purchase(app=A, tier=TierFour, months=12)` from `BandwidthManager` on some chain, crediting a large, long-lived subscription into `Allowance[chain][A]` (`modules/pallets/bandwidth/src/lib.rs:467-486`).
3. Attacker, from any chain with a registered manager, calls `purchase(app=A, tier=TierOne, months=1, chain=Y)` 1024 times (any `app`/`chain` is accepted; `on_accept` never checks the caller owns `A`, `modules/pallets/bandwidth/src/lib.rs:454-489`).
4. Each call appends via `push_subscription`; once `Allowance[Y][A]` reaches 1024 entries, subsequent pushes evict index 0 — after enough calls, victim `A`'s TierFour subscription (originally at/near the head) is evicted, firing `SubscriptionEvicted { lost_bytes: <large unused balance> }` (`modules/pallets/bandwidth/src/lib.rs:416-434`).
5. App `A`'s prepaid bandwidth is permanently lost even though it was never consumed by legitimate traffic. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L153-200)
```text
    function purchase(bytes calldata app, uint256 tier, uint256 months, bytes calldata chain)
        external
        returns (bytes32 commitment)
    {
        if (app.length == 0 || app.length > MAX_APP_LENGTH || chain.length == 0 || months == 0) {
            revert InvalidPurchase();
        }
        uint256 price18d = tierPrice[tier];
        if (price18d == 0) revert UnknownTier();

        uint256 total18d = price18d * months;
        address feeToken = IDispatcher(_host).feeToken();
        uint8 dec = IERC20Metadata(feeToken).decimals();
        uint256 scale = 10 ** (18 - dec);
        if (total18d % scale != 0) revert PriceNotRepresentable();
        uint256 amount = total18d / scale;

        IERC20(feeToken).safeTransferFrom(msg.sender, address(this), amount);

        BandwidthPurchaseMsg memory body = BandwidthPurchaseMsg({
            app: app,
            tier: tier,
            months: months,
            chain: chain
        });

        commitment = IDispatcher(_host).dispatch(
            DispatchPost({
                dest: IDispatcher(_host).hyperbridge(),
                to: PALLET_BANDWIDTH_MODULE_ID,
                body: abi.encode(body),
                timeout: 0,
                fee: 0,
                payer: address(this)
            })
        );

        emit BandwidthPurchased({
            payer: msg.sender,
            feeToken: feeToken,
            tier: tier,
            months: months,
            amountPaid: amount,
            app: app,
            chain: chain,
            commitment: commitment
        });
    }
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
