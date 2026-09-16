### Title
Bandwidth purchases can evict other buyers' unexpired, prepaid Subscriptions with no refund or compensation - ([File: modules/pallets/bandwidth/src/lib.rs])

### Summary
`pallet-bandwidth` stores prepaid bandwidth as a bounded FIFO list (`Allowance<StateMachine, AppKey> -> BoundedVec<Subscription, 1024>`) per `(chain, app)`. Any unprivileged buyer can call `BandwidthManager.purchase()` on an EVM chain, which dispatches a `BandwidthPurchaseMsg` that the pallet credits by appending a new `Subscription` to this list. When the list is already at its 1024-entry cap, the push evicts the oldest entry (`SubscriptionEvicted`) regardless of whether that entry is expired or still has substantial unused `remaining_bytes` and time left on its `expires_at`. This mirrors the reported bug class: a struct representing a user's paid-for, not-yet-consumed value is unconditionally deleted from an array as a side effect of routine protocol activity, permanently destroying value the payer never got to use.

### Finding Description
- `Allowance` is a `StorageDoubleMap<StateMachine, AppKey, SubscriptionList>` where `SubscriptionList = BoundedVec<Subscription, MaxSubscriptions>` (`MAX_SUBSCRIPTIONS = 1024`). [1](#0-0) 
- Documentation states explicitly: "Pushes onto a full list evict the oldest entry and emit `Event::SubscriptionEvicted`," with no distinction made between expired vs. still-valid, unconsumed subscriptions. [2](#0-1) 
- Each `Subscription` carries `remaining_bytes` (unspent value) and `expires_at`; only the gate's drain path is documented to pop entries at zero `remaining_bytes`, and expiry sweeps separately remove only expired entries — but the FIFO cap-eviction on push is unconditional on list length, not on expiry or remaining balance. [3](#0-2) 
- The purchase path is fully permissionless and reachable by any unprivileged caller: `BandwidthManager.purchase()` on EVM pulls the fee token and dispatches an ISMP POST to `pallet-bandwidth`, which on `on_accept` decodes the message and "appends a fresh `Subscription` to the `(app_chain, app)` FIFO list... If the list was at the 1024 cap, the oldest entry is evicted with `SubscriptionEvicted`." [4](#0-3) [5](#0-4) 

The root cause is structurally identical to the reported bug class: a per-user accrual struct (here, `Subscription`, analogous to the reward-token struct) sitting in a bounded array is force-deleted as a side effect of an unrelated, permissionless action (a new purchase by any third party), with no "claim-only"/drain-first safeguard and no compensation to the original payer.

### Impact Explanation
Any account can pay for the cheapest tier repeatedly (1024 times, or fewer if the target app's bucket already has entries) to force-evict the oldest legitimate subscriptions for a targeted `(chain, app)` pair, permanently destroying other users' or the app's prepaid, unconsumed bandwidth allowance — a direct loss of funds paid to `BandwidthManager.purchase()`. Even without malicious intent, organic purchase volume on a popular app can reach the 1024-entry cap and silently evict older, still-valid prepaid capacity, which is worse than the disclosed report's reward-token case because here it can be forced by any unprivileged actor at will (attacker-controlled griefing), not merely triggered by governance removing a token.

### Likelihood Explanation
Reaching this path requires only calling the permissionless `purchase()` function on `BandwidthManager.sol` with a configured tier — no privileged role, governance action, or unusual conditions are needed. The cap (1024) is a fixed, known constant, making the number of transactions required to force an eviction predictable and bounded, and thus practically achievable by any single attacker willing to pay tier-1 prices repeatedly for the cheapest tier against a target `(chain, app)`.

### Recommendation
Do not evict subscriptions purely by list length. Before evicting on a full list, sweep expired entries first (as the gate does at drain time) and only evict truly expired entries; if the list is still full of live (non-expired) subscriptions, either reject the new purchase, allow the list to grow past the soft cap, or refund/carry forward the evicted subscription's `remaining_bytes` (e.g., pro-rated refund to its original payer or extension of the newest subscription) instead of silently discarding unconsumed value.

### Proof of Concept
1. Attacker (or organic traffic) repeatedly calls `BandwidthManager.purchase(app, TIER1, 1, chain)` for the same target `(chain, app)`, each time paying the tier price and triggering `pallet-bandwidth::on_accept` to append a `Subscription`. [5](#0-4) 
2. Once the `(chain, app)` bucket's `SubscriptionList` reaches `MAX_SUBSCRIPTIONS = 1024`, each further purchase evicts the oldest `Subscription` regardless of its `remaining_bytes`/`expires_at`, emitting `SubscriptionEvicted`. [2](#0-1) 
3. If the evicted entry still had significant `remaining_bytes` and time until `expires_at`, that value — paid for by a legitimate buyer (possibly not the attacker) — is permanently lost with no refund path, mirroring the "removed reward token becomes unclaimable" loss-of-funds pattern from the referenced report.

Note: I was unable to locate the exact push/insert function body (e.g., `push_subscription`) implementing this eviction logic in the indexed portion of `modules/pallets/bandwidth/src/lib.rs`; the eviction behavior is confirmed from the pallet's own module-level documentation and the docs page describing `on_accept` credit flow, but a Devin session with full repo access should verify the precise insertion/eviction code path before treating this as fully proven.

### Citations

**File:** modules/pallets/bandwidth/src/lib.rs (L16-30)
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

**File:** modules/pallets/bandwidth/src/types.rs (L94-111)
```rust
/// One purchase, immutable across its lifetime: `remaining_bytes`
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

**File:** docs/content/developers/evm/bandwidth/overview.mdx (L129-134)
```text
**Purchase (per top-up):**

5. **Approve.** Buyer approves the manager for `tier.price × months` scaled to the local fee token's decimals.
6. **Call `purchase()`.** Manager pulls the fee token, encodes a `BandwidthPurchaseMsg { app, tier, months, chain }`, and dispatches an ISMP POST to `pallet-bandwidth` (recipient `"BWMARKET"`) with `timeout: 0` and `fee: 0`. Emits `BandwidthPurchased` with the dispatch commitment.
7. **Deliver.** A relayer carries the message to Hyperbridge.
8. **Credit.** Pallet's `on_accept` checks `request.from` matches the registered manager, decodes the body, looks up `TierConfig`, computes `bytes × months` and `duration_secs × months`, and appends a fresh `Subscription` to the `(app_chain, app)` FIFO list. Emits `BandwidthCredited { app_chain, app, paid_from, tier, bytes, expires_at }`. If the list was at the 1024 cap, the oldest entry is evicted with `SubscriptionEvicted`.
```

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
