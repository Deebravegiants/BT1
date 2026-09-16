## Analysis

The reported bug class — a shared, permissionless accounting pool where any unprivileged actor can cheaply manipulate a counter that other users' funds depend on, permanently destroying their already-paid-for value — maps directly onto `pallet-bandwidth`'s FIFO subscription list.

### Title
Unprivileged Subscription-Queue Griefing Permanently Destroys Other Buyers' Prepaid Bandwidth - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth` credits a shared, permissionless `(app_chain, app)` bandwidth bucket every time *any* caller invokes `BandwidthManager.purchase()` on a registered source chain. There is no restriction tying a purchase to the app owner or to the payer's own identity — anyone can pay to credit any `(chain, app)` pair (this is the explicit "sponsorship" feature). The bucket's `SubscriptionList` is a `BoundedVec` capped at `MAX_SUBSCRIPTIONS` (1024); once full, every new purchase evicts the oldest live subscription and permanently discards its `remaining_bytes`, with no compensation to whoever paid for it.

### Finding Description
`purchase()` in `BandwidthManager.sol` lets any caller pick an arbitrary `app` and `chain` (the credit target), pull the tier price from themselves, and dispatch a `BandwidthPurchaseMsg` to the pallet: [1](#0-0) 

On the pallet side, `on_accept` decodes the message and calls `push_subscription` for the `(msg.chain, key)` target named in the message body — not tied to `request.from`'s identity beyond the manager contract check: [2](#0-1) 

`push_subscription` appends to the FIFO `Allowance` list; when the list is already at the 1024-item cap, it unconditionally evicts index 0 (the oldest subscription) and emits `SubscriptionEvicted` with the destroyed `lost_bytes`: [3](#0-2) 

The pallet's own doc comment acknowledges this is a loss of paid value: "The 1024-cap pushed out the oldest subscription. `lost_bytes` is what the user paid for and won't get to use." [4](#0-3) 

Because purchases are keyed purely by `(app_chain, app)` — the same multi-tenant/sponsorship design documented for legitimate use — any address that knows a victim app's identifier can flood that app's queue with 1024 minimal, cheap tier-1/1-month purchases. Each cheap purchase evicts one older entry from the front of the FIFO, which (being oldest) is the entry closest to being consumed/legitimately drained by the gate but is not necessarily the cheapest — an attacker with modest capital can force out subscriptions that cost the original buyer(s) far more (e.g. bulk tier-4/12-month purchases), permanently destroying that prepaid capacity with `Allowance::<T>::mutate`'s unconditional `list.remove(0)`, no size- or value-based eviction ordering, and no per-payer isolation.

### Impact Explanation
This directly parallels the reported Cosmos bug class: a shared pooled-accounting value (`ValidatorBondShares` there, prepaid `remaining_bytes` here) that legitimate participants rely on can be reduced/evicted by an unprivileged third party at a fraction of the cost of the funds destroyed. Here, the destruction is literal and permanent — evicted subscriptions' `remaining_bytes` are gone, with the `Withdrawn`/dispute path offering no recovery for the paid fee tokens already pulled into the `BandwidthManager` contract on the source chain. A depleted victim app is also denied delivery via `BandwidthGate::try_consume`, since its purchased capacity vanished before it could be drained, which can additionally freeze the app's ability to dispatch ISMP messages until it repurchases — a direct freezing of the app's operational capability funded by already-spent tokens.

### Likelihood Explanation
The attack requires only a `purchase()` call — permissionless, cheap (minimum tier price × 1 month, chosen by the attacker), and repeatable up to 1024 times to fully cycle the FIFO for a targeted `(chain, app)`. No special privileges, timing races, or governance access are needed; the `app`/`chain` targeting is by design open to any payer (sponsorship), which is exactly what makes the griefing path always reachable.

### Recommendation
Do not let an unconditional eviction destroy value paid by a different, unrelated purchase. Options: (1) track subscriptions per-payer and only allow a purchaser's own subscriptions to be evicted by the same purchaser's future purchases; (2) refund/compensate the evicted subscription's remaining value to its original payer before removal, or dispatch a corresponding refund message back to the paying chain; (3) evict by expiry proximity or smallest remaining value rather than strict FIFO insertion order, so cheap flooding cannot target the largest legitimate holdings; or (4) increase `MAX_SUBSCRIPTIONS` bound or add a minimum-purchase-size/cooldown per payer to make flooding economically infeasible relative to the value it displaces.

### Proof of Concept
1. Governance registers a `BandwidthManager` for chain A and configures cheap `Tier 1` (small `bytes`, minimal `price18d`) and expensive `Tier 4` (large `bytes`/`duration_secs`, high price).
2. Victim buyers legitimately purchase several `Tier 4` subscriptions crediting `(app_chain = B, app = VictimApp)`, each occupying a slot near the front of the FIFO once earlier tier-1 filler entries drain/expire.
3. Attacker, with no relationship to `VictimApp`, repeatedly calls `BandwidthManager.purchase(app = VictimApp, tier = 1, months = 1, chain = B)` from chain A — each call cheaply funds itself and dispatches a `BandwidthPurchaseMsg` that the pallet accepts unconditionally per `on_accept`: [2](#0-1) 
4. Once `Allowance::<T>::get(B, VictimApp).len() == MAX_SUBSCRIPTIONS`, each further attacker purchase evicts index `0` via `list.remove(0)` in `push_subscription`, destroying whichever subscription is currently oldest — including the victims' expensive `Tier 4` credits — and emits `SubscriptionEvicted { lost_bytes }` with no refund: [5](#0-4) 
5. The victim's paid fee tokens (already pulled by `BandwidthManager.purchase` on their own source chain) are unrecoverable, and `VictimApp`'s bandwidth balance on chain B is reduced or exhausted, blocking its ISMP dispatches via `BandwidthGate::try_consume`'s `Insufficient`/`NoAllowance` rejection: [6](#0-5)

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L153-188)
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
```

**File:** modules/pallets/bandwidth/src/lib.rs (L168-175)
```rust
		/// The 1024-cap pushed out the oldest subscription. `lost_bytes`
		/// is what the user paid for and won't get to use.
		SubscriptionEvicted {
			app_chain: StateMachine,
			app: AppKey,
			tier: TierIndex,
			lost_bytes: BandwidthBytes,
		},
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

**File:** modules/pallets/bandwidth/src/lib.rs (L467-486)
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

**File:** modules/pallets/bandwidth/src/lib.rs (L509-535)
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

```
