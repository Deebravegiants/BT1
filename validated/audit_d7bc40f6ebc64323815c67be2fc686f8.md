### Title
`swap_and_burn` in the Snowbridge System Frontend pallet performs a permissionless AMM swap with no slippage protection, enabling sandwich attacks - (File: `bridges/snowbridge/pallets/system-frontend/src/lib.rs`)

### Summary
The Snowbridge `system-frontend` pallet's `add_tip` extrinsic is callable by any signed account and internally triggers a token swap through `pallet_asset_conversion`'s `Swap` trait with `amount_out_min` hard-coded to `None`. This is the same root-cause vulnerability class described in the external report (`BuyAndBurn.swap()`): a swap of value through a public AMM pool with no minimum-output/slippage guard, triggered by a call that anyone can invoke at a time of their choosing, is sandwichable by an MEV actor.

### Finding Description
`Pallet::add_tip` is a plain signed extrinsic: [1](#0-0) 

It calls `swap_fee_asset_and_burn`, which — whenever the supplied asset differs from the target `EthereumLocation` (ether) — delegates to `swap_and_burn`: [2](#0-1) 

`swap_and_burn` performs the actual AMM trade via `T::Swap::swap_exact_tokens_for_tokens`, explicitly passing `None` for the minimum-output parameter: [3](#0-2) 

The `Swap` trait's `swap_exact_tokens_for_tokens` (implemented by `pallet-asset-conversion`) accepts an `Option<Balance>` amount-out-minimum specifically to defend against price movement/slippage between quote-time and execution-time: [4](#0-3) [5](#0-4) 

Because the caller of `add_tip` never supplies (and cannot supply) a minimum acceptable output, the amount of ether actually received from swapping the tip asset is whatever the pool's constant-product formula yields at execution time — with no floor. This is functionally identical to `BuyAndBurn.swap()` in the external report: a swap of value through a public two-sided AMM pool, triggered inside a transaction whose net effect (how much gets burned/committed) depends entirely on the pool's spot price at execution, with no protection against price manipulation in the same block.

`register_token` has the same exposure for non-`Here` origins, since it also calls `swap_fee_asset_and_burn`: [6](#0-5) 

### Impact Explanation
An attacker who observes a pending `add_tip` (or `register_token`) call in the transaction pool can:
1. Front-run it with a trade in the same `tip_asset`/ether pool that pushes the price against the victim (reduces the ether output the swap will yield).
2. Let the victim's `swap_exact_tokens_for_tokens(..., None, ...)` execute at the manipulated, unfavorable price — the victim receives (and burns/teleports) less ether than the fair-market value of their tip/fee asset, with no `ProvidedMinimumNotSufficientForSwap` check to abort the trade.
3. Back-run to restore the price, capturing the price-impact spread as risk-free profit.

The victim's `add_tip`/`register_token` call still succeeds (it doesn't revert, unlike a properly slippage-protected swap), so the loss is silent: the amount of ether actually burned/relayed cross-chain (which determines the relayer reward or the teleported value backing the token registration) is degraded below what the user intended to pay, and the difference is extracted by the attacker via the pool trade rather than by the protocol/user. This directly parallels the reported impact class (value extraction via sandwiching a permissionless, unprotected AMM swap), though the specific victim/beneficiary economics differ from the original DeFi contract's burn address.

### Likelihood Explanation
- `add_tip` requires only `ensure_signed` — any account can call it at will, and the swap is triggered synchronously within the same extrinsic, so an attacker can predictably sandwich it in the same block via standard MEV/bundling techniques (this is chain-agnostic; block producers or searchers with same-block ordering power can trivially sandwich any pending extrinsic).
- The `None` minimum is not a bug in a generic sense — it is explicitly written in the code with the comment "No minimum amount required" — indicating the omission of slippage protection was a deliberate design choice, not an oversight, similar to how the original `BuyAndBurn.swap()` finding was "risk accepted" by its team.
- Exploitability depends on liquidity/depth of the specific `tip_asset`/ether pool on whichever runtime configures `T::Swap` as `pallet-asset-conversion`; thinner pools make the attack cheaper and more profitable.

### Recommendation
Add caller-supplied (or governance/config-derived) slippage protection to `swap_and_burn`, e.g. compute an `amount_out_min` from an oracle-independent on-chain quote (`quote_price_exact_tokens_for_tokens`) with a bounded tolerance, or expose a `min_ether_out` parameter on `add_tip`/`register_token` that the caller sets themselves, mirroring how `pallet_asset_conversion::swap_exact_tokens_for_tokens`'s own extrinsic requires `amount_out_min` from the signer. Reverting on excessive slippage (instead of silently accepting a swap at any price) removes the sandwich incentive.

### Proof of Concept
Conceptual, based on the code above (no local repro was executed):
1. A pool exists in `pallet-asset-conversion` between `tip_asset` and the runtime's `EthereumLocation` (ether-representing asset), configured as `T::Swap` for the `system-frontend` pallet.
2. Victim submits `add_tip(message_id, Asset{ id: tip_asset, fun: Fungible(tip_amount) })`.
3. Attacker, seeing this in the pool, submits:
   - Tx A (front-run): swap ether → tip_asset (or tip_asset → ether, depending on desired price direction) in the same pool to shift the price so that `tip_asset → ether` yields less ether than at the true price.
   - Victim's `add_tip` executes `swap_exact_tokens_for_tokens(tip_amount, None, ...)`, receiving a reduced `ether_gained` that is then burned via `burn_for_teleport` — no revert occurs because there is no floor.
   - Tx B (back-run): attacker reverses Tx A, restoring the pool price and pocketing the price-impact spread taken from the victim's swap.
4. Net effect: victim's tip is honored on-chain (extrinsic succeeds) but the relayer reward / registration fee value backing it on Ethereum is lower than intended; attacker profits the difference via the two bracketing trades.

### Citations

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L225-252)
```rust
		pub fn register_token(
			origin: OriginFor<T>,
			asset_id: Box<VersionedLocation>,
			metadata: AssetMetadata,
			fee_asset: Asset,
		) -> DispatchResult {
			ensure!(!Self::export_operating_mode().is_halted(), Error::<T>::Halted);

			let asset_location: Location =
				(*asset_id).try_into().map_err(|_| Error::<T>::UnsupportedLocationVersion)?;
			let origin_location = T::RegisterTokenOrigin::ensure_origin(origin, &asset_location)?;

			let ether_gained = if origin_location.is_here() {
				// Root origin/location does not pay any fees/tip.
				0
			} else {
				Self::swap_fee_asset_and_burn(origin_location.clone(), fee_asset)?
			};

			let call = Self::build_register_token_call(
				origin_location.clone(),
				asset_location,
				metadata,
				ether_gained,
			)?;

			Self::send_transact_call(origin_location, call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L261-273)
```rust
		pub fn add_tip(origin: OriginFor<T>, message_id: MessageId, asset: Asset) -> DispatchResult
		where
			<T as frame_system::Config>::AccountId: Into<Location>,
		{
			let who = ensure_signed(origin)?;

			let ether_gained = Self::swap_fee_asset_and_burn(who.clone().into(), asset)?;

			// Send the tip details to BH to be allocated to the reward in the Inbound/Outbound
			// pallet
			let call = Self::build_add_tip_call(who.clone(), message_id.clone(), ether_gained);
			Self::send_transact_call(who.into(), call)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L290-317)
```rust
		fn swap_and_burn(
			origin: Location,
			tip_asset_location: Location,
			ether_location: Location,
			tip_amount: u128,
		) -> Result<u128, DispatchError> {
			// Swap tip asset to ether
			let swap_path = vec![tip_asset_location.clone(), ether_location.clone()];
			let who = T::AccountIdConverter::convert_location(&origin)
				.ok_or(Error::<T>::LocationConversionFailed)?;

			let ether_gained = T::Swap::swap_exact_tokens_for_tokens(
				who.clone(),
				swap_path,
				tip_amount,
				None, // No minimum amount required
				who,
				true,
			)?;

			// Burn the ether
			let ether_asset = Asset::from((ether_location.clone(), ether_gained));

			burn_for_teleport::<T::AssetTransactor>(&origin, &ether_asset)
				.map_err(|_| Error::<T>::BurnError)?;

			Ok(ether_gained)
		}
```

**File:** bridges/snowbridge/pallets/system-frontend/src/lib.rs (L372-404)
```rust
		fn swap_fee_asset_and_burn(
			origin: Location,
			fee_asset: Asset,
		) -> Result<u128, DispatchError> {
			let ether_location = T::EthereumLocation::get();
			let (fee_asset_location, fee_amount) = match fee_asset {
				Asset { id: AssetId(ref loc), fun: Fungible(amount) } => (loc, amount),
				_ => {
					tracing::debug!(target: LOG_TARGET, ?fee_asset, "error matching fee asset");
					return Err(Error::<T>::UnsupportedAsset.into());
				},
			};
			if fee_amount == 0 {
				return Ok(0);
			}

			let ether_gained = if *fee_asset_location != ether_location {
				Self::swap_and_burn(
					origin.clone(),
					fee_asset_location.clone(),
					ether_location,
					fee_amount,
				)
				.inspect_err(|&e| {
					tracing::debug!(target: LOG_TARGET, ?e, "error swapping asset");
				})?
			} else {
				burn_for_teleport::<T::AssetTransactor>(&origin, &fee_asset)
					.map_err(|_| Error::<T>::BurnError)?;
				fee_amount
			};
			Ok(ether_gained)
		}
```

**File:** substrate/frame/asset-conversion/src/swap.rs (L93-97)
```rust
	fn swap_exact_tokens_for_tokens(
		path: Vec<Self::AssetKind>,
		credit_in: Self::Credit,
		amount_out_min: Option<Self::Balance>,
	) -> Result<Self::Credit, (Self::Credit, DispatchError)>;
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L980-1002)
```rust
		pub(crate) fn do_swap_exact_tokens_for_tokens(
			sender: T::AccountId,
			path: Vec<T::AssetKind>,
			amount_in: T::Balance,
			amount_out_min: Option<T::Balance>,
			send_to: T::AccountId,
			keep_alive: bool,
		) -> Result<T::Balance, DispatchError> {
			ensure!(amount_in > Zero::zero(), Error::<T>::ZeroAmount);
			if let Some(amount_out_min) = amount_out_min {
				ensure!(amount_out_min > Zero::zero(), Error::<T>::ZeroAmount);
			}

			Self::validate_swap_path(&path)?;
			let path = Self::balance_path_from_amount_in(amount_in, path)?;

			let amount_out = path.last().map(|(_, a)| *a).ok_or(Error::<T>::InvalidPath)?;
			if let Some(amount_out_min) = amount_out_min {
				ensure!(
					amount_out >= amount_out_min,
					Error::<T>::ProvidedMinimumNotSufficientForSwap
				);
			}
```
