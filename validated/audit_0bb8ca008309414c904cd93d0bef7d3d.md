### Title
PSM pallet mints internal-asset debt based on nominal transfer amount without verifying actual reserve credit, enabling insolvency for non-exact-transfer external assets - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
The custom `pallet-psm` (Peg Stability Module) added to this fork mints its internal stablecoin 1:1 against an `external_asset` deposit computed from a *nominal* amount, but never checks that the reserve account actually received that amount. This is the same root-cause class as the Notional `wfCashERC4626` M-14 finding: the vault/pool credits shares/debt based on the amount it *intended* to receive rather than the amount it *actually* received, which can desynchronize total liabilities from actual backing assets.

### Finding Description
In `Pallet::mint` (`substrate/frame/psm/src/lib.rs:702-767`), the flow is: [1](#0-0) 

```rust
T::Fungibles::transfer(
    external_asset.clone(),
    &who,
    &psm_account,
    effective_external,
    Preservation::Expendable,
)?;
T::Fungibles::mint_into(internal_asset.clone(), &who, internal_to_user)?;
```
The return value of `transfer` (which is the actual amount moved) is discarded — only its `Result` is propagated with `?`. `internal_to_user` and `PsmDebt` are then updated purely from the pre-computed `effective_external`/`internal_equivalent`, not from what the reserve account (`psm_account`) actually gained.

`T::Fungibles` is a generic `fungibles::Mutate` bound, and the crate's own default `transfer` implementation is loose about the actual amount moved: it performs `decrease_balance`/`increase_balance` with `BestEffort` precision internally, yet unconditionally returns the *requested* `amount`, not the amount actually credited to the destination: [2](#0-1) 

Because `pallet-assets` does not override `Mutate::transfer` with its own implementation in this codebase (no such override was found in `substrate/frame/assets/src/functions.rs`), any `T::Fungibles` external-asset backend that is not a byte-for-byte "exact debit = exact credit" implementation (e.g. a bridged/foreign-asset adapter, a bespoke fungibles impl for a non-Substrate-native token, or any implementation with deflationary/fee/dust-shaving semantics) can legally transfer less than `effective_external` into `psm_account` while `Pallet::mint` still mints the full `internal_to_user` and records the full debt increase.

The same discard-the-actual-amount pattern appears symmetrically in `redeem`: [3](#0-2) 

### Impact Explanation
If any approved `external_asset` on a PSM instance is backed by a `T::Fungibles` implementation whose transfer can deliver less than the requested amount to `psm_account` (fee-bearing, deflationary, or otherwise non-exact fungible implementations — plausible for bridged/foreign assets on a parachain), then `PsmDebt` (the pallet's own bookkeeping of "internal asset minted, backed 1:1 by reserve") will exceed the external asset actually held in `psm_account`. Since `internal_to_user` is minted to depositors regardless of the shortfall, the internal asset's total outstanding claim against that PSM instance becomes larger than its real backing. On `redeem`, the pallet does defensively check `reserve < external_out` and reverts with `Error::Unexpected` (`substrate/frame/psm/src/lib.rs:851-855`), but this only prevents any single redemption from over-drawing the depleted reserve — it does not fix the underlying deficit. The practical effect is that some accumulated internal-asset holders (particularly the last ones queued to redeem, analogous to the wfCash "last depositor" scenario) become permanently unable to redeem their full claim, and the PSM instance is left insolvent relative to its own recorded debt.

### Likelihood Explanation
The `mint`/`redeem` extrinsics themselves are fully permissionless and callable by any unprivileged user — the vulnerable code path executes on every single mint. The only precondition is that a PSM instance has an approved `external_asset` whose `T::Fungibles` transfer semantics do not guarantee "amount requested == amount credited" (added via `add_external_asset`, a semi-privileged but ordinary protocol-configuration action, not root/governance compromise). Given that FRAME's own generic `fungibles::Mutate::transfer` default (used absent a pallet-assets override) already only best-effort-moves balances while still reporting the nominal `amount`, and that the PSM pallet is explicitly designed to be asset-agnostic (`T::Fungibles` is generic, intended to support arbitrary/bridged assets), this is a realistic integration risk rather than a purely theoretical one, closely mirroring the real-world Notional incident where the vault was designed generically to support arbitrary ERC-20s including fee-on-transfer tokens.

### Recommendation
1. In `Pallet::mint`, capture the `Balance` returned by `T::Fungibles::transfer(...)` and use that *actual* transferred amount (converted back through `external_to_internal`) to compute `internal_equivalent`/`internal_to_user`/`PsmDebt` increments, instead of the pre-computed `effective_external`.
2. Symmetrically in `redeem`, verify the amount actually delivered by the outgoing `T::Fungibles::transfer` to the user matches `external_out` before finalizing debt/burn accounting, or reconcile any shortfall against the caller rather than the pool.
3. Consider adding an explicit invariant check/flag per external asset declaring whether its `T::Fungibles` implementation guarantees exact transfers, and reject `add_external_asset` for assets that cannot provide this guarantee, analogous to the wfCash fix of disallowing lend-at-zero for fee-on-transfer underlyings.

### Proof of Concept
Conceptual sequence (cannot be executed against real `pallet-assets`, which is exact-transfer only in this repo, but demonstrates the code-level flaw against any non-exact `T::Fungibles` impl configured as an external asset):
1. Configure a PSM instance's `external_asset` to a `T::Fungibles` backend where `transfer(from, psm_account, X, ...)` only credits `psm_account` with `X - fee` (e.g., due to BestEffort dust handling or a deflationary/foreign-asset adapter).
2. Call `Psm::mint(origin, internal_asset, external_asset, X, max_fee)`.
3. `effective_external = X` (assuming zero minting fee), the pallet mints `internal_to_user = X` (in internal decimals) to the caller and increases `PsmDebt` by `X`, while `psm_account`'s actual external balance only increased by `X - fee`.
4. Repeat across many mints; `PsmDebt` grows faster than the real reserve balance.
5. When redemptions are attempted for the full `PsmDebt`, the last redeemers hit `reserve < external_out` and `Error::Unexpected` (`substrate/frame/psm/src/lib.rs:851-855`), unable to redeem — the PSM instance is insolvent for that external asset pair.

### Citations

**File:** substrate/frame/psm/src/lib.rs (L743-756)
```rust
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

**File:** substrate/frame/psm/src/lib.rs (L878-887)
```rust
			let psm_account = Self::psm_account(&internal_asset);
			if !external_out.is_zero() {
				T::Fungibles::transfer(
					external_asset.clone(),
					&psm_account,
					&who,
					external_out,
					Preservation::Expendable,
				)?;
			}
```

**File:** substrate/frame/support/src/traits/tokens/fungibles/regular.rs (L366-386)
```rust
	fn transfer(
		asset: Self::AssetId,
		source: &AccountId,
		dest: &AccountId,
		amount: Self::Balance,
		preservation: Preservation,
	) -> Result<Self::Balance, DispatchError> {
		let _extra = Self::can_withdraw(asset.clone(), source, amount)
			.into_result(preservation != Expendable)?;
		Self::can_deposit(asset.clone(), dest, amount, Extant).into_result()?;
		if source == dest {
			return Ok(amount);
		}

		Self::decrease_balance(asset.clone(), source, amount, BestEffort, preservation, Polite)?;
		// This should never fail as we checked `can_deposit` earlier. But we do a best-effort
		// anyway.
		let _ = Self::increase_balance(asset.clone(), dest, amount, BestEffort);
		Self::done_transfer(asset, source, dest, amount);
		Ok(amount)
	}
```
