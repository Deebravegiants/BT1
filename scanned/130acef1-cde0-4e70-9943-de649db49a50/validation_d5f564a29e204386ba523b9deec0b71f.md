### Title
PSM pallet lacks price-oracle protection against depegged collateral, enabling fee-bounded arbitrage that drains higher-value external assets from a multi-collateral PSM instance - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` implements a Peg Stability Module that lets multiple external stablecoins (e.g. USDC, USDT, DAI) be minted/redeemed against a single internal stablecoin at a fixed 1:1 rate, adjusted only by a static `Permill` fee — never by a live market price. This is the same "fee-less (bounded-by-fee) swap" primitive described in the LevelMinting report: any external asset can be swapped for any other external asset held in the same PSM instance's reserve via `mint` then `redeem`, with no oracle check on the actual value of either asset. If one approved external stablecoin depegs beyond the fee corridor, an unprivileged arbitrageur can drain the reserve of the still-pegged asset(s), leaving the PSM instance holding the worthless one.

### Finding Description
`pallet-psm::mint` deposits `external_amount` of an approved external asset and mints the internal asset 1:1 (minus `MintingFee`), and `pallet-psm::redeem` burns internal asset and pays out a different (or the same) approved external asset 1:1 (minus `RedemptionFee`) — see [1](#0-0)  and [2](#0-1) .

Both operations use only decimal-scaling conversion helpers (`external_to_internal` / `internal_to_external`) and static fee percentages from `MintingFee`/`RedemptionFee` storage — there is no oracle, price feed, or any other market-price input anywhere in the pallet, confirmed by the absence of any "oracle"/"price feed" reference in `substrate/frame/psm/src/lib.rs`. A single PSM instance can hold multiple approved externals simultaneously (`ExternalAssets` keyed by `(internal_asset, external_asset)`), as documented: "A PSM may approve multiple externals, each identified by `asset_id`" [3](#0-2) .

The pallet's own documentation acknowledges the arbitrage corridor is bounded purely by fees, not by any price-awareness of individual collateral assets: "With 0.5% fees on both sides, arbitrage opportunities exist when the internal asset trades outside $0.995-$1.005" [4](#0-3) . This framing only accounts for the internal asset's peg drifting; it does not address the case where one of several approved *external* collateral assets itself depegs (e.g., a USDT/USDC-style de-peg event), which is exactly the LevelMinting scenario. Because mint and redeem are two independent extrinsics with no cooldown, timelock, or same-block restriction in the pallet, a user can call `mint(asset=A)` then `redeem(asset=B)` back-to-back (or in the same block/transaction via a batch), converting depegged asset `A` into internal asset and then draining healthy asset `B` from the shared reserve at the fixed 1:1 rate minus only the configured fee.

### Impact Explanation
If any approved external asset in a PSM instance depegs by more than `MintingFee + RedemptionFee` (default 0.5%+0.5% = 1%, per README [5](#0-4) ), an unprivileged attacker can:
1. Acquire the depegged asset `A` cheaply on the open market.
2. `mint` internal asset against `A` at the fixed 1:1 rate (only losing the minting fee).
3. `redeem` that internal asset for the healthy asset `B` from the same PSM instance's shared reserve at the fixed 1:1 rate (only losing the redemption fee).

This nets the attacker the price difference between `A` and `B`, and systematically drains the PSM instance's reserve of the healthy collateral while accumulating the worthless one — directly mirroring the LevelMinting impact where "the LevelMinting contract will be left with a stablecoin of lower value as a higher-value one will be redeemed by MEV/arbitragers," and in severe depeg events (e.g. a TerraUSD-style crash) this can rapidly exhaust the good collateral for the entire PSM instance, harming redemption capacity for all other holders of the internal asset.

### Likelihood Explanation
This requires no privileged role — `mint` and `redeem` are both `ensure_signed` extrinsics callable by any account [6](#0-5) [7](#0-6) . Multi-collateral PSM instances with more than one approved external asset are an explicit, supported configuration (tested in `multiple_assets_share_redistributed_ceiling` and `mixed_decimal_mint_redeem_cycles_round_trip_to_zero_debt`) [8](#0-7) . Whether the vulnerability manifests depends on runtime configuration (whether a given deployment actually approves multiple externals per instance, and the size of the fee corridor relative to realistic depeg events), but the pallet itself provides no oracle-based safeguard, unlike the fixed LevelMinting contract which discounts mint/redeem amounts using Chainlink price feeds.

### Recommendation
Add an oracle-based price check (or per-asset admin-controlled circuit breaker triggered off-chain/governance monitoring) so that `mint`/`redeem` amounts are adjusted (or the asset's circuit breaker is auto-flipped) when an external asset's live price deviates from $1 beyond a safe threshold — mirroring the fix Level Money applied (discounting minted/redeemed amounts based on Chainlink oracle price). At minimum, document prominently that operators must actively monitor collateral pegs and immediately call `set_asset_status` to `AllDisabled`/`MintingDisabled` on any depegging external asset, since the existing `MintingFee`/`RedemptionFee` corridor is not a substitute for real-time price protection when multiple externals share a reserve.

### Proof of Concept
1. Configure a PSM instance for internal asset `pUSD` with two approved externals, `USDC` (weight 50%) and `USDT` (weight 50%), each with default 0.5% mint/redeem fees (as in `multiple_assets_share_redistributed_ceiling` setup) [9](#0-8) .
2. Assume `USDT` depegs to $0.90 on the open market (a >1% deviation, exceeding the combined 1% fee corridor).
3. Attacker buys 1,000,000 `USDT` for $900,000 on the open market.
4. Attacker calls `Psm::mint(internal_asset=pUSD, external_asset=USDT, external_amount=1_000_000, max_fee=0.5%)` — per [10](#0-9) , receives ~995,000 `pUSD` (1,000,000 minus 0.5% fee), depositing the depegged `USDT` into the shared reserve.
5. Attacker calls `Psm::redeem(internal_asset=pUSD, external_asset=USDC, internal_amount=995,000, max_fee=0.5%)` — per [11](#0-10) , receives ~990,025 `USDC` (worth ~$990,025) from the PSM's healthy reserve, burning the `pUSD`.
6. Net result: attacker spent $900,000 to obtain ~$990,025 of `USDC`, profiting ~$90,000 (minus ~1% total fees), while the PSM instance is left holding 1,000,000 depegged `USDT` (now worth $900,000) in place of the `USDC` it lost — reproducing the LevelMinting-style collateral drain.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L700-754)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::mint(T::MaxExternals::get()))]
		pub fn mint(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			external_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;

			let external = ExternalAssets::<T>::get(&internal_asset, &external_asset)
				.ok_or(Error::<T>::UnsupportedAsset)?;
			ensure!(external.status.allows_minting(), Error::<T>::MintingStopped);

			let (ext_decimals, internal_decimals) =
				Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?;

			let internal_equivalent =
				Self::external_to_internal(external_amount, ext_decimals, internal_decimals)?;
			ensure!(!internal_equivalent.is_zero(), Error::<T>::AmountTooSmallAfterConversion);
			ensure!(internal_equivalent >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let effective_external =
				Self::internal_to_external(internal_equivalent, ext_decimals, internal_decimals)?;

			let fee_rate = MintingFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_equivalent);
			let internal_to_user = internal_equivalent.saturating_sub(fee);

			let current_total_psm_debt = Self::total_psm_debt(&internal_asset);
			ensure!(
				current_total_psm_debt.saturating_add(internal_equivalent) <= info.max_debt,
				Error::<T>::ExceedsMaxPsmDebt
			);

			let current_debt = PsmDebt::<T>::get(&internal_asset, &external_asset);
			let max_debt = Self::max_asset_debt(&internal_asset, &external_asset, &info);
			let new_debt = current_debt.saturating_add(internal_equivalent);
			ensure!(new_debt <= max_debt, Error::<T>::ExceedsMaxPsmDebt);

			let psm_account = Self::psm_account(&internal_asset);
			T::Fungibles::transfer(
				external_asset.clone(),
				&who,
				&psm_account,
				effective_external,
				Preservation::Expendable,
			)?;
			T::Fungibles::mint_into(internal_asset.clone(), &who, internal_to_user)?;
			if !fee.is_zero() {
				T::Fungibles::mint_into(internal_asset.clone(), &info.fee_destination, fee)?;
			}
```

**File:** substrate/frame/psm/src/lib.rs (L809-836)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::redeem())]
		pub fn redeem(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			internal_amount: BalanceOf<T>,
			max_fee: Permill,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let info = Psm::<T>::get(&internal_asset).ok_or(Error::<T>::PsmNotFound)?;

			let external = ExternalAssets::<T>::get(&internal_asset, &external_asset)
				.ok_or(Error::<T>::UnsupportedAsset)?;
			ensure!(external.status.allows_redemption(), Error::<T>::AllSwapsStopped);

			let ext_decimals = external.decimals;
			let internal_decimals = info.internal_decimals;

			ensure!(internal_amount >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let fee_rate = RedemptionFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_amount);
			let internal_net = internal_amount.saturating_sub(fee);

			let external_out =
				Self::internal_to_external(internal_net, ext_decimals, internal_decimals)?;
```

**File:** substrate/frame/psm/README.md (L17-20)
```markdown
- **External** — third-party assets (e.g. USDC, USDT) approved on a
  specific PSM via `add_external_asset` and held in that PSM's reserve. Users
  deposit external to mint internal, and burn internal to redeem external. A
  PSM may approve multiple externals, each identified by `asset_id`.
```

**File:** substrate/frame/psm/README.md (L90-91)
```markdown
With 0.5% fees on both sides, arbitrage opportunities exist when the internal
asset trades outside $0.995-$1.005.
```

**File:** substrate/frame/psm/README.md (L188-189)
```markdown
| `MintingFee`         | Fee for external → internal (per pair)       | 0.5%                    |
| `RedemptionFee`      | Fee for internal → external (per pair)       | 0.5%                    |
```

**File:** substrate/frame/psm/src/tests.rs (L1833-1849)
```rust
	#[test]
	fn multiple_assets_share_redistributed_ceiling() {
		new_test_ext().execute_with(|| {
			// Add a third asset
			let bridged_usdc_asset_id = 4u32;
			create_asset_with_metadata(bridged_usdc_asset_id);
			assert_ok!(Psm::add_external_asset(
				RuntimeOrigin::root(),
				INTERNAL_ASSET_ID,
				bridged_usdc_asset_id
			));

			// Setup: USDC 50%, USDT 25%, ETH:USDC 25%
			set_max_debt(10_000_000 * INTERNAL_UNIT);
			set_asset_ceiling_weight(USDC_ASSET_ID, Permill::from_percent(50));
			set_asset_ceiling_weight(USDT_ASSET_ID, Permill::from_percent(25));
			set_asset_ceiling_weight(bridged_usdc_asset_id, Permill::from_percent(25));
```
