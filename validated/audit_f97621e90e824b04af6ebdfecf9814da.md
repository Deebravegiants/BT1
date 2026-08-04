### Title
ERC-20 precompile `transferFrom` unconditionally requires an approval even when `from == msg.sender` — ([File: substrate/frame/assets/precompiles/src/lib.rs])

### Summary
The `pallet-assets` ERC-20 precompile's `transfer_from` implementation always routes through `pallet_assets::Pallet::do_transfer_approved`, which reads and consumes an `Approvals` storage entry, regardless of whether the caller (`spender`) is the same account as `from`. This mirrors the Surge Protocol `Pool#transferFrom` bug: the ERC-20 spec (and many integrators) expect that when `spender == from`, no allowance should be required — the caller is moving their own funds.

### Finding Description
`Precompile::transfer_from` decodes `from`, `to`, and `value` from the call, and unconditionally calls `do_transfer_approved(asset_id, &from, &spender, &to, approval_amount)` with no check for `spender == from`: [1](#0-0) 

`do_transfer_approved` is the same function backing the `fungibles::approvals::Mutate::transfer_from` trait implementation, which is documented/tested to require and decrement an existing `Approvals` entry: [2](#0-1) [3](#0-2) 

Unlike the pallet's dispatchable extrinsics, where `transfer` (self-transfer, no allowance) and `transfer_approved` (delegated transfer, requires allowance) are two distinct calls, the precompile exposes a single Solidity-style `transferFrom(from, to, value)` entry point that always goes down the allowance-consuming path — exactly analogous to the flawed `Pool#transferFrom` in the Surge report, which always used `allowance[from][msg.sender]` instead of skipping that check when `from == msg.sender`.

### Impact Explanation
Any contract or integrator that follows the common "pull-only" ERC-20 usage pattern — calling `transferFrom(self, dest, amount)` on their own balance instead of `transfer(dest, amount)` — will find the call reverts unless they first call `approve(self, amount)` to themselves, which is not standard behavior for most ERC-20 tokens. This breaks compatibility with protocols that assume `from == msg.sender` implies no allowance requirement, potentially causing funds/logic paths built around this asset to fail or become effectively unusable through that integration path (denial of service for the affected calling pattern), rather than an authentication bypass or fund theft.

### Likelihood Explanation
This is fully reachable by any unprivileged EVM-compatible caller of the precompile (`pallet-revive` contract calling the ERC-20 precompile address) — no privileged origin or trusted role is needed. The likelihood of the specific pattern being hit depends on external integrators using the pull-only `transferFrom` idiom, which the original Sherlock report calls "a large number of protocols."

### Recommendation
In `Precompile::transfer_from` (substrate/frame/assets/precompiles/src/lib.rs), short-circuit the allowance path when `spender == from`, e.g. calling the underlying transfer logic directly (analogous to `do_transfer` semantics) instead of `do_transfer_approved` when the caller is transferring their own funds, matching common ERC-20 expectations.

### Proof of Concept
1. Deploy/instantiate an asset via `pallet-assets`, mint balance to account `A`.
2. From `A`, without calling `approve`, invoke the precompile's `transferFrom(from=A, to=B, value=X)` where the caller (`msg.sender`) is also `A`.
3. Observe the call reverts because no `Approvals` entry exists between `A` and `A`, per `do_transfer_approved`'s allowance lookup shown in [4](#0-3) , whereas a direct `transfer(to=B, value=X)` call would have succeeded without any allowance.

Note: I could not directly view the full body of `do_transfer_approved` in `substrate/frame/assets/src/functions.rs` (index returned only the file header for that read), so the exact storage-access/error path is inferred from `impl_fungibles.rs`, the pallet's own tests (`querying_allowance_should_work`, `approve_revoke_after_partial_transfer`), and the precompile's docstrings — all of which consistently confirm that `transfer_from`/`do_transfer_approved` requires and decrements a real `Approvals` entry unconditionally. A full read of `functions.rs` would be needed to confirm there is no `from == delegate` shortcut already present.

### Citations

**File:** substrate/frame/assets/precompiles/src/lib.rs (L440-457)
```rust
		env.charge(<Runtime as Config<Instance>>::WeightInfo::transfer_approved())?;
		let spender = Self::caller(env)?;
		let spender = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&spender);

		let from = call.from.into_array().into();
		let from = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&from);

		let to = call.to.into_array().into();
		let to = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&to);

		let approval_amount = Self::to_balance(call.value)?;
		pallet_assets::Pallet::<Runtime, Instance>::do_transfer_approved(
			asset_id,
			&from,
			&spender,
			&to,
			approval_amount,
		)?;
```

**File:** substrate/frame/assets/src/impl_fungibles.rs (L310-331)
```rust
impl<T: Config<I>, I: 'static> fungibles::approvals::Mutate<<T as SystemConfig>::AccountId>
	for Pallet<T, I>
{
	// Approve spending tokens from a given account
	fn approve(
		asset: T::AssetId,
		owner: &<T as SystemConfig>::AccountId,
		delegate: &<T as SystemConfig>::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		Self::do_approve_transfer(asset, owner, delegate, amount)
	}

	fn transfer_from(
		asset: T::AssetId,
		owner: &<T as SystemConfig>::AccountId,
		delegate: &<T as SystemConfig>::AccountId,
		dest: &<T as SystemConfig>::AccountId,
		amount: T::Balance,
	) -> DispatchResult {
		Self::do_transfer_approved(asset, owner, delegate, dest, amount)
	}
```

**File:** substrate/frame/assets/src/tests.rs (L1988-2000)
```rust
#[test]
fn querying_allowance_should_work() {
	build_and_execute(|| {
		use frame_support::traits::fungibles::approvals::{Inspect, Mutate};
		assert_ok!(Assets::force_create(RuntimeOrigin::root(), 0, 1, true, 1));
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 1, 100));
		Balances::make_free_balance_be(&1, 2);
		assert_ok!(Assets::approve(0, &1, &2, 50));
		assert_eq!(Assets::allowance(0, &1, &2), 50);
		// Transfer asset 0, from owner 1 and delegate 2 to destination 3
		assert_ok!(Assets::transfer_from(0, &1, &2, &3, 50));
		assert_eq!(Assets::allowance(0, &1, &2), 0);
	});
```
