# [M] Storage can be bloated with low liquidtiy positions

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-acala
Published: 2024-04-02
Source: https://github.com/code-423n4/2024-03-acala-findings/issues/17
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-03-acala/blob/9c71c05cf2d9f0a2603984c50f76fc8a315d4d65/src/modules/incentives/src/lib.rs#L230


# Vulnerability details

## Impact

The `deposit_dex_share` function enforce no minimum amount that can be deposited into the pool allows for creating multiple pool positions. This causes that in a coordinated effort, for a pretty cheap cost, users/attackers can create multiple low liquidity positions to bloat the runtime storage. This is very important as substrate framework requires optimization of storage to prevent bloat which can lead to high maintenance costs for the chain and a potential DOS. A more in detail explanation can be found [here](https://docs.substrate.io/build/troubleshoot-your-code/#storage).

## Proof of Concept

The test case below shows how a user can create multiple 1 wei positions, and it can be added to [test.rs](https://github.com/code-423n4/2024-03-acala/blob/main/src/modules/incentives/src/tests.rs).
```rust
#[test]
fn open_low_liquidity_positions() {
	ExtBuilder::default().build().execute_with(|| {
		assert_ok!(TokensModule::deposit(BTC_AUSD_LP, &ALICE::get(), 1000000000));
		assert_eq!(TokensModule::free_balance(BTC_AUSD_LP, &ALICE::get()), 1000000000);
		assert_eq!(
			TokensModule::free_balance(BTC_AUSD_LP, &IncentivesModule::account_id()),
			0
		);
		assert_eq!(RewardsModule::pool_infos(PoolId::Dex(BTC_AUSD_LP)), PoolInfo::default(),);
		assert_eq!(
			RewardsModule::shares_and_withdrawn_rewards(PoolId::Dex(BTC_AUSD_LP), ALICE::get()),
			Default::default(),
		);
		assert_ok!(IncentivesModule::deposit_dex_share(
			RuntimeOrigin::signed(ALICE::get()),
			BTC_AUSD_LP,
			1
		));
		assert_ok!(IncentivesModule::deposit_dex_share(
			RuntimeOrigin::signed(ALICE::get()),
			BTC_AUSD_LP,
			1
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-acala-findings/issues/17_
