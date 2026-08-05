Based on my investigation, I found a legitimate analog to this vulnerability class in `substrate/frame/psm/src/lib.rs`, but with important caveats explained below.

### Title
`fee_destination` in `pallet-psm` is not validated for blocked/frozen status, allowing an admin-set fee-collection account to permanently DoS `mint`/`redeem` extrinsics - (File: `substrate/frame/psm/src/lib.rs`)

### Summary
`pallet-psm` (Peg Stability Module) implements a fixed-rate swap between an "internal" stablecoin and approved "external" assets. Each PSM instance stores a `fee_destination: T::AccountId` in `PsmInfo`, set at `create_psm` and used as the mandatory recipient of minting/redemption fees in the `mint` and `redeem` extrinsics.

### Finding Description
In `mint`, if the computed fee is non-zero, the pallet unconditionally mints fee tokens into `info.fee_destination` via `T::Fungibles::mint_into(...)?` [1](#0-0) . In `redeem`, the fee is transferred to `info.fee_destination` via `T::Fungibles::transfer(...)?` [2](#0-1) . Both use the `?` operator, so any failure of the fee-recipient operation aborts the whole extrinsic and reverts all storage changes (standard FRAME dispatch-error rollback semantics), just like the RubiconMarket `buy` function reverting on a failed `feeTo` transfer.

`fee_destination` is set by `create_psm`, which is gated by `Config::CreateOrigin` (e.g., the asset owner) rather than by unprivileged callers [3](#0-2) . I found no `set_fee_destination` extrinsic in the portion of the file I was able to read, so `fee_destination` appears fixed for the life of a PSM instance and is only chosen once by a privileged (asset-owner/root) actor.

Unlike the Solidity `RubiconMarket` case (an ERC20 explicitly reverting on transfers to `address(0)`), the FRAME/`pallet-assets` transfer and mint primitives do not revert simply because the destination is the all-zero `AccountId`. Instead, failures would arise from asset-account-level conditions such as: the destination account being **frozen/blocked** for that asset (`Error::Frozen`/`TokenError::Blocked`, as demonstrated in `substrate/frame/assets/src/tests.rs` lines 852-864 and 866-880), the destination lacking the existential deposit and the transfer being `Expendable`... (actually `Expendable` should allow creation, but the account could still fail to be created if it has no provider references and the asset is not "sufficient"), or if the `fee_destination` asset account had previously been fully destroyed. Because `create_psm` calls `frame_system::Pallet::<T>::inc_providers(&fee_destination)` to keep it alive [4](#0-3) , the most plausible route to a stuck fee recipient is the destination account being frozen or blocked at the asset level by whoever controls the `Freezer`/admin role for that specific asset — which is a distinct actor from the PSM's own admin.

### Impact Explanation
If `fee_destination`'s asset account for the internal asset becomes frozen or blocked (by the asset's freezer/admin, independent of the PSM admin), every subsequent `mint` and `redeem` call that would produce a non-zero fee reverts with `Error::Frozen`/`TokenError::Blocked`, permanently denying service to the PSM's mint/redeem functionality for all users until the destination account is unblocked. This mirrors the RubiconMarket DoS pattern (privileged-but-unvalidated recipient blocks unprivileged users' core function calls).

### Likelihood Explanation
Likelihood is low-to-moderate and requires a precondition outside an unprivileged attacker's control: someone with asset-freezer/admin privileges over the *internal asset* must freeze/block the specific `fee_destination` account. This is not attacker-reachable by an ordinary, unprivileged user acting alone — it depends on either an admin misconfiguration or a compromised/malicious asset-freezer role, and the "trusted-role compromise required" disqualifier from the scan rules is closer to applying here than a fully unprivileged DoS. I could not read the remainder of the file (e.g., any `set_fee_destination`/`transfer_fee_destination` call) to confirm whether the PSM's own `full_admin` can freely reassign `fee_destination` to an already-known-bad account; the file was too large to view in full via the tool, and I was only able to inspect lines 1-1250 of 1745 total lines. This limits full confirmation of the exact set of admin/attacker capabilities.

### Recommendation
- Before crediting/transferring fees to `fee_destination`, verify the destination asset account is not frozen/blocked (or use a fee-forwarding path with graceful degradation, e.g., skip/queue the fee rather than reverting the whole swap).
- Consider decoupling fee failure from the swap's success: attempt the fee transfer with `Precision::BestEffort`/non-propagating error handling (as `substrate/frame/treasury` and `substrate/frame/tips` do with `debug_assert!`-guarded "best effort" transfers) so that fee-recipient issues cannot block core user-facing functionality.
- If a `set_fee_destination`-style extrinsic exists further in the file (unverified), require validating that the new destination is a healthy, unfrozen/unblocked account for the internal asset at the time of the update, and consider periodic re-validation.

### Proof of Concept
Because I could not confirm the presence/absence of a runtime call to change `fee_destination` after creation, and because triggering the freeze requires a second, non-PSM privileged role (the internal asset's `Freezer`), I cannot provide a concrete, fully unprivileged proof-of-concept. The mechanical trigger, conditional on that admin action, is:
1. `full_admin`/asset owner creates a PSM via `create_psm` with `fee_destination = X` and a non-zero `MintingFee`/`RedemptionFee` for some `(internal, external)` pair.
2. The internal asset's `Freezer` role calls `Assets::freeze`/`Assets::block` on account `X` for the internal asset (per `substrate/frame/assets/src/lib.rs` `freeze`/`block` calls and semantics shown in `substrate/frame/assets/src/tests.rs` lines 852-880).
3. Any unprivileged user calling `Psm::mint` or `Psm::redeem` with a non-zero resulting fee now has their `mint_into`/`transfer` to `X` fail and the entire extrinsic revert, permanently DoS-ing `mint`/`redeem` for that PSM instance until `X` is thawed/unblocked. [5](#0-4) [6](#0-5)

### Citations

**File:** substrate/frame/psm/src/lib.rs (L280-292)
```rust
	pub struct PsmInfo<T: Config> {
		/// Account receiving minting and redemption fees, denominated in the internal asset.
		pub fee_destination: T::AccountId,
		/// This PSM instance's debt ceiling, in internal-asset units.
		pub max_debt: BalanceOf<T>,
		/// Minimum swap amount for this instance, in internal-asset units. Swaps whose
		/// internal-equivalent falls below this are rejected with [`Error::BelowMinimumSwap`].
		pub min_swap_amount: BalanceOf<T>,
		/// Snapshot of the internal asset's decimals at install time.
		pub internal_decimals: u8,
		/// Number of approved external assets attached to this instance.
		pub external_count: u32,
	}
```

**File:** substrate/frame/psm/src/lib.rs (L751-754)
```rust
			T::Fungibles::mint_into(internal_asset.clone(), &who, internal_to_user)?;
			if !fee.is_zero() {
				T::Fungibles::mint_into(internal_asset.clone(), &info.fee_destination, fee)?;
			}
```

**File:** substrate/frame/psm/src/lib.rs (L857-865)
```rust
			if !fee.is_zero() {
				T::Fungibles::transfer(
					internal_asset.clone(),
					&who,
					&info.fee_destination,
					fee,
					Preservation::Expendable,
				)?;
			}
```

**File:** substrate/frame/psm/src/lib.rs (L942-957)
```rust
		pub fn create_psm(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			full_admin: Box<T::PalletsOrigin>,
			emergency_admin: Box<T::PalletsOrigin>,
			fee_destination: T::AccountId,
			max_debt: BalanceOf<T>,
			min_swap_amount: BalanceOf<T>,
		) -> DispatchResult {
			let maybe_depositor = T::CreateOrigin::ensure_origin(origin, &internal_asset)?;
			ensure!(!Psm::<T>::contains_key(&internal_asset), Error::<T>::PsmAlreadyExists);
			ensure!(!min_swap_amount.is_zero(), Error::<T>::ZeroMinSwapAmount);
			ensure!(
				T::Fungibles::asset_exists(internal_asset.clone()),
				Error::<T>::AssetDoesNotExist
			);
```

**File:** substrate/frame/psm/src/lib.rs (L987-993)
```rust
			// Acquire a provider reference on the reserve account and the fee destination for the
			// lifetime of this PSM, so they can hold non-sufficient assets (external collateral /
			// minted fees). Released in `remove_psm`. Unconditional (rather than
			// `ensure_account_exists`) so the inc/dec is symmetric even when an account already
			// exists or is shared across PSMs.
			frame_system::Pallet::<T>::inc_providers(&Self::psm_account(&internal_asset));
			frame_system::Pallet::<T>::inc_providers(&fee_destination);
```

**File:** substrate/frame/assets/src/tests.rs (L866-880)
```rust
#[test]
fn transferring_to_blocked_account_should_not_work() {
	build_and_execute(|| {
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 2, 100));
		assert_eq!(Assets::balance(0, 1), 100);
		assert_eq!(Assets::balance(0, 2), 100);
		assert_ok!(Assets::block(RuntimeOrigin::signed(1), 0, 1));
		assert_noop!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 50), TokenError::Blocked);
		assert_ok!(Assets::thaw(RuntimeOrigin::signed(1), 0, 1));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(2), 0, 1, 50));
		assert_ok!(Assets::transfer(RuntimeOrigin::signed(1), 0, 2, 50));
	});
}
```
