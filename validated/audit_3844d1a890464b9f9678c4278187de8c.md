## Analysis

The reported bug class — an unprivileged caller supplies an unvalidated, free-form identifier (`_message`) that irreversibly determines the destination of a paid effect, with no on-chain correctness check and no refund path if the caller gets it wrong — maps directly onto `BandwidthManager.purchase()`, an unprivileged bandwidth-purchaser entry point in Hyperbridge's EVM apps.

### Title
Unvalidated `app`/`chain` identifiers in `BandwidthManager.purchase()` allow permanent loss of purchaser funds on a fat-fingered or malformed recipient — (File: evm/src/apps/BandwidthManager.sol)

### Summary
`BandwidthManager.purchase()` lets any caller pay a tier price in the fee token to credit bandwidth to an arbitrary `(chain, app)` pair. The `app` and `chain` parameters are purely caller-supplied bytes: the contract only checks length/emptiness, never that `app` corresponds to a real, controllable recipient, and dispatches an irreversible cross-chain credit message. Once dispatched, the payment cannot be recovered if the identifier was wrong.

### Finding Description
`purchase()` pulls the exact tier cost from the caller via `safeTransferFrom`, then dispatches a `BandwidthPurchaseMsg{app, tier, months, chain}` to `pallet-bandwidth` on Hyperbridge: [1](#0-0) 

The only validation performed on `app`/`chain` is non-emptiness and a max length bound: [2](#0-1) 

There is no check that `app` is a real, existing, or caller-controlled recipient identifier, and no check that `chain` is even a sensible target beyond being non-empty bytes (parsing/validation of `chain` happens only later, off-chain-adjacent, in the pallet). On the receiving side, `pallet-bandwidth::on_accept` simply truncates whatever bytes were supplied into an `AppKey` and credits that bucket — it cannot detect a typo'd or malformed `app`: [3](#0-2) [4](#0-3) 

Documentation confirms this is by design (sponsorship of any chain/app is intentional), but the same design has no correction/refund mechanism for buyer error: the `chain` argument is explicitly "not validated against the source chain," and credit is keyed purely by the values inside the message body: [5](#0-4) 

This is structurally identical to the reported `FootiumGeneralPaymentContract.makePayment()` bug: an off-chain/cross-domain side effect (feature unlock vs. bandwidth credit) is entirely keyed by an arbitrary, unchecked, user-supplied identifier, with the payment already collected and non-refundable by the time any mismatch could be noticed.

### Impact Explanation
If a buyer supplies a malformed, mistyped, or otherwise incorrect `app` byte string (e.g., wrong padding, wrong address, truncated/garbled bytes) or an unintended `chain`, the fee-token payment is irrecoverably taken by the `BandwidthManager` and the credit lands on a `(chain, app)` bucket that the buyer cannot control or drain — the pallet has no mechanism to reassign or refund a misdirected `BandwidthCredited` subscription. This is a direct, permanent loss of the buyer's paid funds, with no on-chain recourse. Governance can issue an admin-only `force_credit` as a manual remedy, but this is neither automatic nor guaranteed, and the protocol itself provides no correctness check or refund at dispatch time.

### Likelihood Explanation
`purchase()` is fully unprivileged and reachable by any address holding the fee token; the only prerequisites (registered manager, configured tier) are ordinary operating conditions, not attacker-controlled gates. Buyer error (copy/paste mistakes, wrong `app` encoding for a non-EVM destination, incorrect `chain` string) is a realistic and common class of user mistake, especially since `app` is raw `bytes` rather than a typed `address`, and `chain` is a free-form UTF-8 string with no client-side or on-chain cross-check against the actual deployment being funded.

### Recommendation
Add stronger on-chain guardrails before value leaves the buyer's control: e.g., require `app` to decode to a well-formed address for EVM chain ids and echo/validate it against a caller-confirmed value, validate `chain` against an allow-list of known/supported credit chains at purchase time (reverting rather than silently accepting arbitrary bytes), and/or add a buyer-initiated cancellation/refund window before the ISMP dispatch is finalized. At minimum, expose a governance-gated refund path keyed by the dispatch commitment so misdirected purchases are recoverable without relying solely on discretionary `force_credit`.

### Proof of Concept
1. Buyer calls `purchase(app, tier, months, chain)` with a fee-token approval in place.
2. `app` is supplied as a malformed/incorrect byte string (e.g., missing leading zero, wrong length within `MAX_APP_LENGTH`, or an address the buyer does not actually control on the target chain), or `chain` is set to a chain id string that does not correspond to where the buyer's app actually lives.
3. `purchase()` passes the `app.length != 0 && app.length <= 32 && chain.length != 0 && months != 0` check at `evm/src/apps/BandwidthManager.sol:157-159`, pulls the exact tier cost via `safeTransferFrom`, and dispatches the `BandwidthPurchaseMsg`.
4. `pallet-bandwidth::on_accept` (`modules/pallets/bandwidth/src/lib.rs:454-489`) decodes the message, truncates `app` into `AppKey`, and credits a `Subscription` to `(chain, AppKey)` — a bucket the buyer cannot access or reclaim.
5. The buyer's fee-token payment is spent with no refund path; the credited subscription is functionally unusable by the intended party.

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

**File:** modules/pallets/bandwidth/src/abi.rs (L20-31)
```rust
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

**File:** docs/content/developers/evm/bandwidth/overview.mdx (L108-114)
```text
## Sponsorship

The purchase message carries its own `chain` (the _credit chain_) which is **independent of the source chain** that sent the message. This means a buyer on Ethereum can credit an app on Base by dispatching a purchase whose payload sets `chain = "EVM-8453"`.

The pallet keys allowance storage by `(app_chain, app)` taken from the message body, not by `request.source`. The event `BandwidthCredited` carries both — `app_chain` (where the credit lands) and `paid_from` (where the payment came from) — so the cross-chain payer is auditable.

This is what makes the system multi-tenant friendly: a treasury on a single chain can sponsor bandwidth for an app deployed across many chains, without having to deploy `BandwidthManager` on each chain the app lives on.
```
