The code and test exactly match the claim. Analysis confirms:

1. `do_refund_other` unconditionally checks `account.balance.is_zero()` with no `allow_burn` override [1](#0-0) , unlike `do_refund` which accepts `allow_burn` [2](#0-1) .
2. Transfers/mints of an asset are permissionless for any holder of that asset, so a third party (attacker) can send a trivial nonzero amount to the target account to keep `balance.is_zero()` false.
3. The existing regression test explicitly documents this exact failure mode as intended behavior ("fail case; would burn") [3](#0-2) .
4. The admin can bypass this by force-`burn`-ing the balance before calling `refund_other`, as shown right after the failing assertion in the same test [4](#0-3) , confirming the block is recoverable via privileged intervention, not a permanent fund lock.

This matches the report's own characterization: a low-severity griefing/DoS on deposit-reclamation timing, recoverable by the asset admin, not an unrecoverable loss of funds. This is a legitimate, reproducible finding rooted in an actual code path with a real asymmetry between `do_refund` and `do_refund_other`, not a speculative or mocked scenario.

Audit Report

## Title
`WouldBurn` strict-zero-balance check in `do_refund_other` allows griefing of existence-deposit reclamation - (File: `substrate/frame/assets/src/functions.rs`)

## Summary
`do_refund_other`, used by the `refund_other` extrinsic to let a depositor/admin reclaim a `DepositFrom` existence deposit on behalf of another account, unconditionally requires the target account's balance to be zero, with no `allow_burn` override unlike its self-service counterpart `do_refund`. Because asset transfers/mints are permissionless for any holder of the asset, a third party can indefinitely block the refund by repeatedly dusting the target account with a nonzero balance.

## Finding Description
`do_refund_other` enforces `ensure!(account.balance.is_zero(), Error::<T, I>::WouldBurn)` with no way to force a burn [5](#0-4) , whereas `do_refund` accepts an `allow_burn` flag that lets the caller force-clear a nonzero balance and unblock the refund [6](#0-5) . Since any holder of the asset can call the permissionless `transfer` extrinsic to send an arbitrary (even 1-unit) amount into the target account, an attacker who is neither the depositor, admin, nor freezer can make `account.balance.is_zero()` false and cause `refund_other` to fail with `Error::WouldBurn` repeatedly. The existing test suite documents this exact behavior as the expected "fail case; would burn" [7](#0-6) .

## Impact Explanation
This is a griefing/DoS on deposit reclamation, not a loss of principal or accounting break. The depositor's reserved existence deposit can be kept locked as long as the griefer keeps re-dusting the account, but the asset's admin retains a recovery path via the privileged `burn` extrinsic to zero the balance before calling `refund_other` again, as demonstrated immediately after the failing assertion in the same test [4](#0-3) . This bounds the severity to a low-impact, recoverable inconvenience rather than a permanent fund lock.

## Likelihood Explanation
Triggering the griefing requires only that (a) a `DepositFrom`-reason account exists (via `touch_other`) that someone wants to reclaim, and (b) the attacker holds any nonzero amount of the same asset to transfer — both trivially satisfiable for any permissionless asset. Repeatability is straightforward since re-dusting after every honest resolution attempt is cheap, but resolution via privileged `burn` remains available at any time to the admin.

## Recommendation
Add an `allow_burn`-style parameter (or equivalent forced-burn path) to `refund_other`/`do_refund_other`, mirroring the self-service `refund` extrinsic's `allow_burn` flag, so a depositor/admin can force-clear dust balances and reclaim the deposit without requiring a separate privileged `burn` call.

## Proof of Concept
1. Admin/depositor `X` calls `Assets::touch_other(origin, asset_id, victim)` to create an asset account for `victim` and reserve a deposit.
2. Attacker `Y`, holding units of `asset_id`, calls `Assets::transfer(origin, asset_id, victim, 1)` (permissionless for any holder of the asset).
3. `X` calls `Assets::refund_other(origin, asset_id, victim)` → fails with `Error::<T>::WouldBurn`, reproducible via the existing test `refund_other_frozen` at [7](#0-6) ; the admin can bypass by calling `burn` first as shown at [4](#0-3) .

### Citations

**File:** substrate/frame/assets/src/functions.rs (L371-379)
```rust
	pub(super) fn do_refund(id: T::AssetId, who: T::AccountId, allow_burn: bool) -> DispatchResult {
		use AssetStatus::*;
		use ExistenceReason::*;

		let mut account = Account::<T, I>::get(&id, &who).ok_or(Error::<T, I>::NoDeposit)?;
		ensure!(matches!(account.reason, Consumer | DepositHeld(..)), Error::<T, I>::NoDeposit);
		let mut details = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
		ensure!(matches!(details.status, Live | Frozen), Error::<T, I>::IncorrectStatus);
		ensure!(account.balance.is_zero() || allow_burn, Error::<T, I>::WouldBurn);
```

**File:** substrate/frame/assets/src/functions.rs (L418-432)
```rust
	pub(super) fn do_refund_other(
		id: T::AssetId,
		who: &T::AccountId,
		maybe_check_caller: Option<T::AccountId>,
	) -> DispatchResult {
		let mut account = Account::<T, I>::get(&id, &who).ok_or(Error::<T, I>::NoDeposit)?;
		let (depositor, deposit) =
			account.reason.take_deposit_from().ok_or(Error::<T, I>::NoDeposit)?;
		let mut details = Asset::<T, I>::get(&id).ok_or(Error::<T, I>::Unknown)?;
		ensure!(details.status == AssetStatus::Live, Error::<T, I>::AssetNotLive);
		ensure!(!account.status.is_frozen(), Error::<T, I>::Frozen);
		if let Some(caller) = maybe_check_caller {
			ensure!(caller == depositor || caller == details.admin, Error::<T, I>::NoPermission);
		}
		ensure!(account.balance.is_zero(), Error::<T, I>::WouldBurn);
```

**File:** substrate/frame/assets/src/tests.rs (L1247-1253)
```rust
		// fail case; would burn
		assert_ok!(Assets::mint(RuntimeOrigin::signed(1), 0, 3, 100));
		assert_noop!(
			Assets::refund_other(RuntimeOrigin::signed(1), 0, 3),
			Error::<Test>::WouldBurn
		);
		assert_ok!(Assets::burn(RuntimeOrigin::signed(1), 0, 3, 100));
```
