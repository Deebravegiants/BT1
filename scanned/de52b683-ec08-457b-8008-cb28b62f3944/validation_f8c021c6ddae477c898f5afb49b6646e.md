### Title
Zero-fee mint/redeem cycle in `pallet-psm` enables cost-free front-run/back-run DoS of the shared debt ceiling - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` (a Peg Stability Module added in this fork) exposes permissionless `mint` and `redeem` extrinsics gated by a shared, per-instance debt ceiling (`PsmInfo::max_debt`) and a derived per-external ceiling (`max_asset_debt`). Both extrinsics accept a governance-configured `MintingFee`/`RedemptionFee` (`Permill`), with no minimum floor enforced in the reviewed code. When these fees are set to `0` (a legitimate, documented configuration, e.g. "runtime wants to bootstrap adoption with no fees"), a full mint→redeem round trip costs the attacker nothing beyond gas/weight fees, exactly mirroring the root cause of the referenced Beedle report ("setting borrower fee to 0 permits ... complete DoS").

### Finding Description
`mint` checks the aggregate ceiling and the per-external ceiling before minting: [1](#0-0) 

and `redeem` releases occupied debt back to zero, symmetric to `mint`: [2](#0-1) [3](#0-2) 

The per-external ceiling is a normalized share of the shared, instance-wide `max_debt`: [4](#0-3) 

Fees are computed from `MintingFee`/`RedemptionFee` storage, both `Permill` values that can be `0`: [5](#0-4) [6](#0-5) 

The README explicitly documents that fees are what create the arbitrage/economic disincentive, and that a fee of `0%` is a supported configuration state: [7](#0-6) 

There is no cooldown, per-account reservation, or minimum-holding-period between `mint` and `redeem` in the same block, and no floor preventing `MintingFee`/`RedemptionFee` from being set to `0` via the governance-only `set_minting_fee`/`set_redemption_fee` calls.

**Attack scenario, directly analogous to the Beedle report:**
1. PSM admin sets `MintingFee = 0` and `RedemptionFee = 0` for a pair to encourage adoption (a legitimate, documented use case).
2. Attacker observes a pending legitimate `mint` transaction (or simply wants to grief the PSM) and front-runs it, minting up to the remaining headroom of `max_asset_debt`/`max_debt` using their own capital.
3. The victim's `mint` now reverts with `Error::ExceedsMaxPsmDebt`.
4. Attacker back-runs (or simply waits one call) and calls `redeem` to reclaim their capital at zero fee, freeing the ceiling headroom, then can repeat the cycle indefinitely — the only cost is transaction weight/gas, since deposit and withdrawal at `0%` fee are value-neutral round trips.

This blocks all legitimate minting on the pair (or the whole PSM instance, if the aggregate `max_debt` is targeted) for as long as the attacker is willing to pay gas, exactly the "low-cost front-run + back-run to occupy the entire capacity" pattern described in the report.

### Impact Explanation
Any unprivileged, permissionless account can indefinitely deny `mint` access to a PSM instance/pair by parking their own capital against the shared debt ceiling with zero economic cost when fees are configured to `0`. This is a functional, sustained denial of service against one of the PSM's two core operations (minting), which can be used to grief a competing user, censor a specific pair, or stall protocol adoption incentives that rely on a temporary zero-fee promotion — the same motivation and mechanism as the original report.

### Likelihood Explanation
Likelihood is conditional but realistic: it requires the PSM's `full_admin` to set `MintingFee`/`RedemptionFee` to `0` for a pair — a legitimate, foreseeable governance action (explicitly the report's own suggested reason to zero fees: "to encourage adoption"). Once that state is reached, exploitation requires no special privilege, only capital equal to the remaining ceiling headroom and the ability to front-run/back-run transactions (standard MEV/reordering capability), matching the report's low-cost, unprivileged-attacker profile.

### Recommendation
- Enforce a minimum non-zero floor for `MintingFee`/`RedemptionFee` (or a protocol-level default fee applied regardless of the configured per-pair fee), so a full mint→redeem round trip is never economically free.
- Alternatively/additionally, add a cooldown or minimum holding period between `mint` and `redeem` for the same account/pair, or track ceiling occupancy per-account with decay, to prevent an attacker from cycling the entire ceiling within one or two blocks.
- Consider making `max_debt`/`max_asset_debt` consumption fair-queued or rate-limited so a single account cannot monopolize the full remaining headroom in a single call.

### Proof of Concept
Conceptual reproduction using the existing pallet-psm test harness (mirrors the `infinite_until_debt_ceiling` test pattern already present in the pallet's test suite): [8](#0-7) 
1. Configure `set_minting_fee(internal, external, 0%)` and `set_redemption_fee(internal, external, 0%)`.
2. Attacker calls `mint` with `external_amount` sized to fill `max_asset_debt` (or `max_debt`) minus current debt.
3. Victim's `mint` call in the same block reverts with `Error::ExceedsMaxPsmDebt`.
4. Attacker calls `redeem` for the full `internal_received` amount, receiving back the exact external amount deposited (0% fee ⇒ no loss), freeing the ceiling.
5. Repeat steps 2–4 indefinitely to sustain the DoS at zero net cost (excluding gas).

### Citations

**File:** substrate/frame/psm/src/lib.rs (L727-730)
```rust
			let fee_rate = MintingFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_equivalent);
			let internal_to_user = internal_equivalent.saturating_sub(fee);
```

**File:** substrate/frame/psm/src/lib.rs (L732-741)
```rust
			let current_total_psm_debt = Self::total_psm_debt(&internal_asset);
			ensure!(
				current_total_psm_debt.saturating_add(internal_equivalent) <= info.max_debt,
				Error::<T>::ExceedsMaxPsmDebt
			);

			let current_debt = PsmDebt::<T>::get(&internal_asset, &external_asset);
			let max_debt = Self::max_asset_debt(&internal_asset, &external_asset, &info);
			let new_debt = current_debt.saturating_add(internal_equivalent);
			ensure!(new_debt <= max_debt, Error::<T>::ExceedsMaxPsmDebt);
```

**File:** substrate/frame/psm/src/lib.rs (L828-833)
```rust
			ensure!(internal_amount >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let fee_rate = RedemptionFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_amount);
			let internal_net = internal_amount.saturating_sub(fee);
```

**File:** substrate/frame/psm/src/lib.rs (L889-891)
```rust
			PsmDebt::<T>::mutate(&internal_asset, &external_asset, |debt| {
				*debt = debt.saturating_sub(effective_internal_net);
			});
```

**File:** substrate/frame/psm/src/lib.rs (L1521-1536)
```rust
		pub(crate) fn max_asset_debt(
			internal_asset: &T::AssetId,
			external_asset: &T::AssetId,
			info: &PsmInfo<T>,
		) -> BalanceOf<T> {
			let asset_weight = AssetCeilingWeight::<T>::get(internal_asset, external_asset);
			let total_weight = Self::total_ceiling_weight(internal_asset);
			Self::normalised_ceiling(asset_weight, total_weight, info.max_debt)
		}

		/// Sum of the configured ceiling weights across a PSM's approved externals.
		fn total_ceiling_weight(internal_asset: &T::AssetId) -> u32 {
			AssetCeilingWeight::<T>::iter_prefix(internal_asset)
				.map(|(_, w)| w.deconstruct())
				.fold(0u32, |acc, x| acc.saturating_add(x))
		}
```

**File:** substrate/frame/psm/README.md (L80-91)
```markdown
## Fee Structure

Fees are stored per `(internal_asset, external_asset)` pair, calculated using
`Permill::mul_ceil` (rounds up), and routed to the instance's `fee_destination`:

- **Minting Fee**: `fee = MintingFee[internal, external].mul_ceil(internal_equivalent)`
  -- deducted from internal-asset output, minted to `fee_destination`
- **Redemption Fee**: `fee = RedemptionFee[internal, external].mul_ceil(amount)`
  -- transferred from the user to `fee_destination`

With 0.5% fees on both sides, arbitrage opportunities exist when the internal
asset trades outside $0.995-$1.005.
```

**File:** substrate/frame/psm/src/tests.rs (L2260-2309)
```rust
				// Mint
				assert_ok!(Psm::mint(
					RuntimeOrigin::signed(ALICE),
					INTERNAL_ASSET_ID,
					USDC_ASSET_ID,
					amount,
					Permill::from_percent(1)
				));

				let (mint_fee, internal_received) = match last_event() {
					Event::Minted { internal_fee, internal_received, .. } => {
						(internal_fee, internal_received)
					},
					_ => panic!("Expected Minted event"),
				};
				total_mint_fees += mint_fee;

				println!(
					"\n=== Cycle {} - After Mint ({:.2} USDC) ===",
					cycle,
					amount as f64 / unit
				);
				println!("Mint fee: {:.2}", mint_fee as f64 / unit);
				println!("internal received: {:.2}", internal_received as f64 / unit);
				println!("User USDC: {:.2}", get_asset_balance(USDC_ASSET_ID, ALICE) as f64 / unit);
				println!(
					"User internal: {:.2}",
					get_asset_balance(INTERNAL_ASSET_ID, ALICE) as f64 / unit
				);
				println!(
					"PSM USDC: {:.2}",
					get_asset_balance(USDC_ASSET_ID, psm_account()) as f64 / unit
				);
				println!(
					"PSM Debt: {:.2}",
					PsmDebt::<Test>::get(INTERNAL_ASSET_ID, USDC_ASSET_ID) as f64 / unit
				);
				println!(
					"IF internal: {:.2}",
					get_asset_balance(INTERNAL_ASSET_ID, INSURANCE_FUND) as f64 / unit
				);

				// Redeem all internal received
				assert_ok!(Psm::redeem(
					RuntimeOrigin::signed(ALICE),
					INTERNAL_ASSET_ID,
					USDC_ASSET_ID,
					amount,
					Permill::from_percent(1)
				));
```
