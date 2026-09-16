## Title
`BandwidthManager.purchase()` pulls buyer payment with no refund path when the destination pallet permanently rejects the credit - (File: `evm/src/apps/BandwidthManager.sol`)

### Summary
`BandwidthManager.purchase()` charges the buyer's fee token immediately and dispatches an ISMP POST with `timeout: 0` to `pallet-bandwidth`. If `pallet_bandwidth::on_accept` cannot credit the purchase for a *permanent* (non-retryable) reason — most notably `UnknownManager`/`UnauthorizedManager` because governance hasn't yet (or no longer) registered this exact manager address for the source chain, or `UnknownTier`/tier-not-configured because the two sides' tier tables have drifted — the buyer's tokens sit in the `BandwidthManager` contract forever. There is no permissionless refund, no timeout, and the only path to move those funds is a privileged, governance-only `Withdraw` message from `pallet-bandwidth`.

### Finding Description
`purchase()` in `evm/src/apps/BandwidthManager.sol` pulls the scaled tier price from the caller before any cross-chain confirmation that the purchase will actually be credited: [1](#0-0) 

The dispatched request uses `timeout: 0`: [2](#0-1) 

`pallet-bandwidth`'s `IsmpModule::on_timeout` explicitly treats any timeout firing as an invariant violation rather than a valid refund path — purchases are documented as "non-timeouting": [3](#0-2) 

On the destination side, `on_accept` rejects the credit outright (returning an `Err`, which is a hard failure, not a retryable success) in several cases that an unprivileged buyer can trigger simply by calling `purchase()` against a manager whose on-chain configuration is out of sync with the pallet: [4](#0-3) 

Concretely:
- The manager contract only checks `tierPrice[tier] != 0` locally before pulling funds — it has no way to know whether `pallet-bandwidth::BandwidthManager::<T>::get(source)` has actually been set to *this* manager's address, or has been changed to a different address by governance (e.g. during a re-deploy/migration). If `set_manager` hasn't landed yet, or has been repointed, `on_accept` returns `UnknownManager`/unauthorized-sender error for every purchase from that manager. [5](#0-4) 
- Likewise, tier prices live on the manager (`tierPrice[tier]`) while tier byte/duration configs live on the pallet (`Tiers<T>`), and the two are only synced by a governance `dispatch_set_tiers`/`set_tier` call. A manager can have a non-zero `tierPrice[tier]` (so `purchase()` succeeds and funds are pulled) while the pallet's `Tiers::<T>::get(tier)` is `None` (unconfigured or since revoked), which returns `UnknownTier`/"tier is not configured" and rejects the credit. [6](#0-5) 

Because `on_accept` failure is a hard error (not something the ISMP router retries indefinitely as a delivery-layer issue) and `timeout: 0` disables the normal timeout/refund mechanism, the buyer has no on-chain way to reclaim the fee tokens already sitting in `BandwidthManager`. The only exit is `onAccept`'s `Withdraw` action, which can only be triggered by a `pallet-bandwidth` governance-origin call (`dispatch_withdraw`, gated by `AdminOrigin`): [7](#0-6) [8](#0-7) 

This mirrors the `saleRecipient`-rug bug class: value flows from an unprivileged buyer directly into a contract's custody without any escrow-and-release-on-delivery guarantee or self-service refund, leaving the buyer dependent entirely on a third party (here, Hyperbridge governance) to make them whole.

### Impact Explanation
Any buyer's `purchase()` payment (up to the $1000/8MB tier price, multiplied by `months`) can become permanently stuck in `BandwidthManager` with no self-service recovery, constituting a freezing-of-funds condition for the affected buyer. This is exactly the "misconfiguration window" the docs themselves flag as a normal, expected operational state ("Until every step lands, purchases fail — usually `UnknownManager` (pallet) or `UnknownTier()` (manager)"), meaning the vulnerable window is not a hypothetical edge case but part of the documented deployment/bring-up and tier-migration lifecycle. Funds recovery then depends entirely on Hyperbridge governance noticing and issuing a `dispatch_withdraw`, which is not guaranteed and not something the buyer can force or verify will happen for their specific loss.

### Likelihood Explanation
Likelihood is realistic rather than contrived: the documentation itself describes bring-up as a multi-step, non-atomic process (`setHost` → `set_manager` → `set_tier` → `dispatch_set_tiers`) during which purchases against a partially configured manager are explicitly expected to fail. Any buyer (or automated integration) calling `purchase()` during this window, or during a tier revocation/migration, or against a re-deployed manager whose registration hasn't been re-pointed on the pallet, hits this exact path with no privileged action required on the attacker/victim side — it's a normal unprivileged call to `purchase()`.

### Recommendation
Do not let `BandwidthManager.purchase()` custody buyer funds unconditionally on a non-timing-out request. Options:
1. Give purchase messages a non-zero timeout and implement `onPostRequestTimeout` in `BandwidthManager` to refund the buyer's fee tokens when the message times out (requires the pallet to also support timing out unresolvable credits instead of treating any timeout as an invariant violation).
2. Add a permissionless `refund()`/`claim()` path in `BandwidthManager` for a purchase whose corresponding delivery/credit never lands within a bounded window, verified via a state/receipt proof from Hyperbridge (analogous to how `IntentGatewayV2`'s escrow refund flow proves non-fill via a storage proof before releasing funds back to the payer).
3. At minimum, have `purchase()` verify (via a view call or cached mirror) that the pallet has actually registered this exact manager address and that the tier is configured on both sides before pulling the fee token, closing the largest practical window for stuck funds, and clearly document any residual risk that still requires governance intervention.

### Proof of Concept
1. Governance deploys `BandwidthManager` on chain X, calls `setHost`, and sets `tierPrice[1]` via a `SetTiers` message — but has not yet (or no longer, after a re-deploy) called `pallet-bandwidth::set_manager(X, managerAddr)`.
2. Buyer approves and calls `manager.purchase(app, 1, 1, "EVM-8453")`. `BandwidthManager.purchase()` succeeds locally: `tierPrice[1] != 0`, so `safeTransferFrom` pulls the buyer's fee tokens into the manager, and `IDispatcher.dispatch(...)` is called with `timeout: 0`. [1](#0-0) 
3. The request reaches `pallet-bandwidth::on_accept`, which looks up `BandwidthManager::<T>::get(source)`, finds `None`, and returns `Err("no bandwidth manager registered for ...")`. [9](#0-8) 
4. No `BandwidthCredited` event is ever emitted; the buyer's app is never credited any bandwidth.
5. Because the dispatch used `timeout: 0`, the message can never time out to trigger a refund path, and `BandwidthManager.sol` implements no `onPostRequestTimeout` override or self-service withdrawal anyway. [3](#0-2) 
6. The buyer's fee-token payment remains locked in `BandwidthManager` until/unless Hyperbridge governance separately notices and issues `dispatch_withdraw` to send it back — an action the buyer cannot compel or verify. [10](#0-9)

### Citations

**File:** evm/src/apps/BandwidthManager.sol (L160-188)
```text
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

**File:** evm/src/apps/BandwidthManager.sol (L220-228)
```text
        } else if (action == OnAcceptActions.Withdraw) {
            Withdrawal memory w = abi.decode(request.body[1:], (Withdrawal));
            if (w.token != address(0)) {
                IERC20(w.token).safeTransfer(w.beneficiary, w.amount);
            } else {
                (bool sent,) = w.beneficiary.call{value: w.amount}("");
                if (!sent) revert InsufficientNativeToken();
            }
            emit Withdrawn(w.token, w.beneficiary, w.amount);
```

**File:** modules/pallets/bandwidth/src/lib.rs (L99-103)
```rust
	/// Authorised purchase contract per source chain. A purchase whose
	/// `request.from` doesn't match this is rejected.
	#[pallet::storage]
	pub type BandwidthManager<T: Config> =
		StorageMap<_, Twox64Concat, StateMachine, H160, OptionQuery>;
```

**File:** modules/pallets/bandwidth/src/lib.rs (L126-130)
```rust
	/// Active tier SKUs keyed by `TierIndex`. Absent (or `None` via
	/// `set_tier`) means the tier is unconfigured; purchases against
	/// it are rejected.
	#[pallet::storage]
	pub type Tiers<T: Config> = StorageMap<_, Twox64Concat, TierIndex, TierConfig, OptionQuery>;
```

**File:** modules/pallets/bandwidth/src/lib.rs (L324-357)
```rust
		/// Push a `Withdraw` message to a remote `BandwidthManager` so
		/// it ships `amount` of `token` to `beneficiary`. Token is
		/// named explicitly because the contract supports recovering
		/// stale fee tokens after a host-side swap.
		#[pallet::call_index(5)]
		#[pallet::weight(T::DbWeight::get().writes(1))]
		pub fn dispatch_withdraw(
			origin: OriginFor<T>,
			target: StateMachine,
			token: H160,
			beneficiary: H160,
			amount: U256,
		) -> DispatchResult {
			<T as pallet_ismp::Config>::AdminOrigin::ensure_origin(origin)?;
			let manager = BandwidthManager::<T>::get(&target).ok_or(Error::<T>::UnknownManager)?;

			let payload = Withdrawal {
				token: alloy_primitives::Address::from(token.0),
				beneficiary: alloy_primitives::Address::from(beneficiary.0),
				amount: to_alloy_u256(amount),
			};
			let mut body = vec![ACTION_WITHDRAW];
			body.extend(payload.abi_encode_params());

			let commitment = Self::dispatch_governance(target, manager, body)?;
			Self::deposit_event(Event::WithdrawalDispatched {
				target,
				token,
				beneficiary,
				amount,
				commitment,
			});
			Ok(())
		}
```

**File:** modules/pallets/bandwidth/src/lib.rs (L454-471)
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
```

**File:** modules/pallets/bandwidth/src/lib.rs (L495-499)
```rust
		/// Purchases dispatch with `timeout = 0`. If `on_timeout` ever
		/// fires it's an invariant violation, not a noop.
		fn on_timeout(&self, _timeout: Request) -> Result<Weight, anyhow::Error> {
			Err(anyhow::anyhow!("pallet-bandwidth purchases are non-timeouting"))
		}
```
