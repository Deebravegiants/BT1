No vulnerability found for this question.

The reported bug class—failing to zero out an ERC-20 allowance before setting a new non-zero value (breaking on tokens like USDT that reject non-zero→non-zero approvals)—does have a direct conceptual analog in this repo: the `approve`/`permit` precompile logic in `pallet-assets-precompiles`. However, that exact issue was already identified and fixed here.

The `approve` function in `substrate/frame/assets/precompiles/src/lib.rs` explicitly implements "set" semantics by calling `do_cancel_approval` before `do_approve_transfer` whenever there is a pre-existing non-zero allowance, which is the equivalent of the report's recommended `safeApprove(..., 0)` pattern. [1](#0-0) 

This was fixed in [2](#0-1)  ("[pallet-assets] Fix ERC-20 approve semantics in precompile"), with the same cancel-then-approve pattern also applied to the `permit` (EIP-2612) path. [3](#0-2) 

Regression tests explicitly cover the non-zero→non-zero overwrite case and confirm the allowance is replaced (not accumulated) and the deposit is handled correctly. [4](#0-3) 

Beyond this precompile, `pallet-assets`'s native `approve_transfer` extrinsic is documented as additive by design (it tops up or unreserves to meet the target value directly, not via a separate "increase allowance on an external token" call), so the USDT-style external-approve-revert scenario from the original report does not apply to it. [5](#0-4) 

There is no code in this repo that calls `safeIncreaseAllowance`/`safeApprove`-style patterns against an external ERC-20-like token contract (the pattern the original Connext report was about), since `pallet-assets` and its precompile *are* the token implementation rather than a caller of one. No unresolved instance of this vulnerability class was found.

### Citations

**File:** substrate/frame/assets/precompiles/src/lib.rs (L396-419)
```rust
		} else {
			// If there's an existing non-zero allowance, cancel it first so we
			// overwrite (not accumulate) — matching ERC-20 spec semantics.
			// NOTE: This does not mitigate the well-known ERC-20 approve front-running
			// race condition. Callers concerned about this should approve to 0 first,
			// or use increaseAllowance/decreaseAllowance if available.
			if !current.is_zero() {
				pallet_assets::Pallet::<Runtime, Instance>::do_cancel_approval(
					&asset_id,
					&owner_account,
					&spender_account,
				)?;
				actual_weight = worst_case;
			} else {
				actual_weight = <Runtime as Config<Instance>>::WeightInfo::allowance()
					.saturating_add(<Runtime as Config<Instance>>::WeightInfo::approve_transfer());
			}
			pallet_assets::Pallet::<Runtime, Instance>::do_approve_transfer(
				asset_id,
				&owner_account,
				&spender_account,
				new_amount,
			)?;
		}
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L533-593)
```rust
				// Delete-set semantic: cancel any existing approval first so
				// do_approve_transfer sets (not accumulates) the new value.
				use frame_support::traits::fungibles::approvals::Inspect as ApprovalsInspect;
				let owner_account =
					<Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&owner_h160);
				let spender_account =
					<Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&spender_h160);

				// Saturate: see `approve` for the rationale (infinite-allowance idiom).
				let new_amount: <Runtime as Config<Instance>>::Balance =
					call.value.unique_saturated_into();
				let current = pallet_assets::Pallet::<Runtime, Instance>::allowance(
					asset_id.clone(),
					&owner_account,
					&spender_account,
				);

				let actual_weight;
				if new_amount.is_zero() {
					if !current.is_zero() {
						// clear approval if it exists, to match ERC-20 semantics of setting
						// allowance to 0
						pallet_assets::Pallet::<Runtime, Instance>::do_cancel_approval(
							&asset_id,
							&owner_account,
							&spender_account,
						)?;
						actual_weight = use_permit_weight
							.saturating_add(<Runtime as Config<Instance>>::WeightInfo::allowance())
							.saturating_add(
								<Runtime as Config<Instance>>::WeightInfo::cancel_approval(),
							);
					} else {
						// noop: set allowance to zerowhen it is already zero
						actual_weight = use_permit_weight
							.saturating_add(<Runtime as Config<Instance>>::WeightInfo::allowance());
					}
				} else {
					if !current.is_zero() {
						// If there's an existing non-zero allowance, cancel it first
						pallet_assets::Pallet::<Runtime, Instance>::do_cancel_approval(
							&asset_id,
							&owner_account,
							&spender_account,
						)?;
						actual_weight = worst_case;
					} else {
						// set new approval
						actual_weight = use_permit_weight
							.saturating_add(<Runtime as Config<Instance>>::WeightInfo::allowance())
							.saturating_add(
								<Runtime as Config<Instance>>::WeightInfo::approve_transfer(),
							);
					}
					pallet_assets::Pallet::<Runtime, Instance>::do_approve_transfer(
						asset_id,
						&owner_account,
						&spender_account,
						new_amount,
					)?;
				}
```

**File:** prdoc/stable2606/pr_11279.prdoc (L1-10)
```text
title: '[pallet-assets] Fix ERC-20 approve semantics in precompile'
doc:
- audience: Runtime Dev
  description: "The ERC-20 approve(spender, amount) spec sets the allowance to amount.\
    \ The precompile was calling do_approve_transfer, which adds to the existing allowance\
    \ \u2014 breaking ERC-20 compliance.\n\nThis PR fixes the precompile's approve\
    \ to use set semantics by composing existing pallet-assets primitives: when\
    \ overwriting a non-zero allowance, the existing approval is cancelled first\
    \ so the new value replaces (not accumulates with) the old one.\n\nAlso extracts\
    \ do_cancel_approval from pallet-assets for reuse by the precompile."
```

**File:** substrate/frame/assets/precompiles/src/tests.rs (L494-536)
```rust
/// Directly overwriting a non-zero allowance with a different non-zero value must use set
/// semantics (cancel + re-approve). The allowance must equal the new value — not the sum of
/// old and new — and only a single deposit should be reserved.
#[test_case(PRECOMPILE_ADDRESS_PREFIX)]
#[test_case(PRECOMPILE_ADDRESS_PREFIX_FOREIGN)]
fn approve_nonzero_to_nonzero(asset_index: u16) {
	use frame_support::traits::fungibles::approvals::Inspect;

	new_test_ext().execute_with(|| {
		let asset_id = 0u32;
		let asset_addr = H160::from(set_prefix_in_address(asset_index));

		let owner = 123456789u64;
		let spender = 987654321u64;

		Balances::make_free_balance_be(&owner, 100);
		Balances::make_free_balance_be(&spender, 100);

		let spender_addr = <Test as pallet_revive::Config>::AddressMapper::to_address(&spender);

		setup_asset_for_prefix(asset_id, asset_index);
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), asset_id, owner, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(owner), asset_id, owner, 100));

		let deposit: u128 = <Test as pallet_assets::Config>::ApprovalDeposit::get();

		// Approve 100 (0 → 100).
		call_approve(owner, asset_addr, spender_addr, U256::from(100));
		assert_eq!(Assets::allowance(asset_id, &owner, &spender), 100);
		assert_eq!(Balances::reserved_balance(&owner), deposit);

		// Overwrite with 50 directly (100 → 50), no zeroing in between.
		call_approve(owner, asset_addr, spender_addr, U256::from(50));
		assert_eq!(Assets::allowance(asset_id, &owner, &spender), 50);
		// Deposit reserved exactly once — cancel unreserved the old one, approve re-reserved.
		assert_eq!(Balances::reserved_balance(&owner), deposit);

		// Overwrite upward (50 → 200) to confirm it works in both directions.
		call_approve(owner, asset_addr, spender_addr, U256::from(200));
		assert_eq!(Assets::allowance(asset_id, &owner, &spender), 200);
		assert_eq!(Balances::reserved_balance(&owner), deposit);
	});
}
```

**File:** substrate/frame/assets/src/lib.rs (L1595-1621)
```rust
		/// Approve an amount of asset for transfer by a delegated third-party account.
		///
		/// Origin must be Signed.
		///
		/// Ensures that `ApprovalDeposit` worth of `Currency` is reserved from signing account
		/// for the purpose of holding the approval. If some non-zero amount of assets is already
		/// approved from signing account to `delegate`, then it is topped up or unreserved to
		/// meet the right value.
		///
		/// NOTE: The signing account does not need to own `amount` of assets at the point of
		/// making this call.
		///
		/// - `id`: The identifier of the asset.
		/// - `delegate`: The account to delegate permission to transfer asset.
		/// - `amount`: The amount of asset that may be transferred by `delegate`. If there is
		/// already an approval in place, then this acts additively.
		///
		/// Emits `ApprovedTransfer` on success.
		///
		/// Weight: `O(1)`
		#[pallet::call_index(22)]
		pub fn approve_transfer(
			origin: OriginFor<T>,
			id: T::AssetIdParameter,
			delegate: AccountIdLookupOf<T>,
			#[pallet::compact] amount: T::Balance,
		) -> DispatchResult {
```
