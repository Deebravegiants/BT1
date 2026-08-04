## Analysis: Valid Analog Found in `pallet-psm`

The Rio `reETH` vulnerability class — multiple assets treated as fungible/interchangeable 1:1 shares in a single pool, letting an attacker deposit a depreciating asset and withdraw a different, unaffected asset — has a direct structural analog in `pallet-psm` (`substrate/frame/psm`).

### Title
Peg Stability Module allows cross-asset value extraction because `mint`/`redeem` convert strictly by decimals, not market value - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` implements a Peg Stability Module where a single internal asset (e.g. a stablecoin/LRT-style token) is backed by a shared pool of multiple approved external assets. Conversion between `internal_asset` and any `external_asset` is computed purely via decimal-precision scaling (`external_to_internal`/`internal_to_external`), assuming the two are worth exactly 1:1 in value. There is no on-chain price check tying the externals to actual market value. If a runtime governance configures a PSM with more than one external asset whose market values are not perfectly co-pegged (which the pallet does not enforce or verify), a user can mint the internal asset against an asset about to lose value, and redeem via a different, more stable asset from the same shared reserve, shifting the loss onto the other holders of the internal asset / other external-asset depositors.

### Finding Description
`mint` (`substrate/frame/psm/src/lib.rs:700-767`) converts an externally-deposited amount to an "internal equivalent" purely through `external_to_internal`, which only rescales by decimal difference: [1](#0-0) 

`redeem` (`substrate/frame/psm/src/lib.rs:809-902`) does the mirror operation, again using only decimal conversion (`internal_to_external`) with no market-price component: [2](#0-1) 

All approved externals on a given `internal_asset` instance share **one reserve account** (`psm_account`), and accounting is tracked purely in internal-asset units via `PsmDebt`: [3](#0-2) 

This is precisely the Rio `reETH` pattern: a single share/debt ledger denominated in one unit, backed by a mix of different underlying assets, where deposits and withdrawals of *different* assets are treated as fungible at a fixed (non-market) rate. The PSM README documents this is intentional for actual stablecoin pegs, and even acknowledges arbitrage incentives from the fee corridor: [4](#0-3) 

However, nothing in the pallet enforces that externals approved on the same instance are actually value-equivalent (there is no oracle, no price feed check, no correlation requirement across `add_external_asset` calls) — the only validation is decimal-range checking: [5](#0-4) 

If a runtime's governance approves two externals whose market prices can diverge (e.g. two different LST/LRT tokens, or an asset expected to depeg/slash), the mechanism becomes directly exploitable exactly as in the Rio report: mint against the depreciating asset while its price is still reflected 1:1, then redeem via the other, unaffected external asset before the loss is otherwise absorbed.

### Impact Explanation
An attacker who anticipates a price drop in one approved external asset (e.g. due to slashing, de-peg, or a scheduled unlock) can:
1. Mint `internal_asset` by depositing the soon-to-drop external asset at the (still-favorable) 1:1-equivalent rate.
2. Immediately redeem the same `internal_asset` for a *different*, unaffected external asset from the shared reserve.
3. Realize the value of the stable/appreciating external asset while leaving the depreciated asset in the shared reserve, effectively socializing the loss to remaining internal-asset holders and future redeemers of the healthy external asset (whose reserve is now smaller relative to outstanding debt).

This mirrors the Medium-severity classification in the Rio report: the attack requires anticipatable price divergence and cannot be executed with a flash loan (capital must be held through the divergence), but is fully executable by an unprivileged, permissionless signed user once governance has approved 2+ externals with any real value volatility.

### Likelihood Explanation
Likelihood depends entirely on runtime configuration: if a PSM instance is deployed for genuinely tightly-pegged stablecoins (its intended design use case), the attack surface is negligible. But the pallet places no on-chain restriction preventing governance from approving externals that are *not* tightly value-correlated, and nothing prevents a future/careless configuration (or an asset that later depegs/slashes after approval) from exposing this exact cross-asset arbitrage. Given `add_external_asset` is a governance action but the resulting `mint`/`redeem` calls are fully permissionless and unprivileged, an attacker only needs monitoring capability (identical to the original Rio report's threat model), not any privileged role.

### Recommendation
- Document/enforce (at minimum via runtime configuration guidance) that PSM instances must only combine externals with tightly correlated, verifiably-pegged market value.
- Consider adding an optional price-deviation guard (oracle-based) that can pause minting/redemption for an external whose market price deviates from its peg beyond a threshold, similar to the existing circuit breaker (`AssetStatus`) but automated rather than purely governance-triggered.
- Consider per-external reserve isolation (rather than a fully shared reserve account) so that a divergence in one external's value cannot be arbitraged against another external's healthy reserve within the same instance.

### Proof of Concept
Given a PSM instance for `internal_asset` with two approved externals `A` and `B`, both currently priced 1:1 against `internal_asset` (per pallet assumption):
1. Attacker observes that `A` is about to lose value (e.g., pending slash/depeg).
2. Attacker calls `mint(internal_asset, A, amount_A, max_fee)` — receives `internal_asset` at the current decimal-only conversion rate [6](#0-5) .
3. Attacker calls `redeem(internal_asset, B, internal_amount, max_fee)` — receives `B` from the shared reserve at the same decimal-only rate [7](#0-6) , before `A`'s price drop is reflected anywhere on-chain (there is no price check to prevent this).
4. `A` subsequently loses value; the PSM reserve for `internal_asset` is now under-collateralized relative to `PsmDebt`, and remaining/future redeemers of `B` (or holders of `internal_asset`) bear the shortfall — this is the same value-transfer mechanism described in the Rio `reETH` report.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L716-725)
```rust
			let (ext_decimals, internal_decimals) =
				Self::ensure_decimals_match(&info, &internal_asset, &external_asset, &external)?;

			let internal_equivalent =
				Self::external_to_internal(external_amount, ext_decimals, internal_decimals)?;
			ensure!(!internal_equivalent.is_zero(), Error::<T>::AmountTooSmallAfterConversion);
			ensure!(internal_equivalent >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let effective_external =
				Self::internal_to_external(internal_equivalent, ext_decimals, internal_decimals)?;
```

**File:** substrate/frame/psm/src/lib.rs (L738-756)
```rust
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

			PsmDebt::<T>::insert(&internal_asset, &external_asset, new_debt);
```

**File:** substrate/frame/psm/src/lib.rs (L825-846)
```rust
			let ext_decimals = external.decimals;
			let internal_decimals = info.internal_decimals;

			ensure!(internal_amount >= info.min_swap_amount, Error::<T>::BelowMinimumSwap);

			let fee_rate = RedemptionFee::<T>::get(&internal_asset, &external_asset);
			ensure!(fee_rate <= max_fee, Error::<T>::FeeTooHigh);
			let fee = fee_rate.mul_ceil(internal_amount);
			let internal_net = internal_amount.saturating_sub(fee);

			let external_out =
				Self::internal_to_external(internal_net, ext_decimals, internal_decimals)?;
			ensure!(
				internal_net.is_zero() || !external_out.is_zero(),
				Error::<T>::AmountTooSmallAfterConversion
			);
			// `effective_internal_net` is the internal value that round-trips to `external_out`;
			// it is what we actually burn and what the tracked debt decreases by. Any truncation
			// dust stays in the caller's internal balance, symmetric with `mint`, which takes
			// only the round-tripped share of the external amount.
			let effective_internal_net =
				Self::external_to_internal(external_out, ext_decimals, internal_decimals)?;
```

**File:** substrate/frame/psm/README.md (L90-91)
```markdown
With 0.5% fees on both sides, arbitrage opportunities exist when the internal
asset trades outside $0.995-$1.005.
```

**File:** substrate/frame/psm/README.md (L146-154)
```markdown
### Asset Onboarding Requirements

Before calling `add_external_asset(internal_asset, asset_id)`:

- A PSM must already be registered for `internal_asset`
- The external `asset_id` must already exist in the `Fungibles` implementation
- The internal asset's live decimals must still match the snapshot in `PsmInfo`
- `|external_decimals − internal_decimals|` must be within `MAX_DECIMALS_DIFF`
- The PSM must still be below `MaxExternals`
```
