# [M] `lastRPS` could be set to `0` accidentally

## Summary
Severity: Medium
Contest weight: 0.7199
Dataset id: 21732
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logic flaw in the way it caches the previous reward rate. When a reward distribution finishes, the internal function _updateEmissions stores the current rewardsPerSecond value into the variable lastRPS and then sets rewardsPerSecond to zero. The subsequent function registerRewardDeposit is designed to restart a new distribution by copying lastRPS back into rewardsPerSecond, but it only does so if rewardsPerSecond is zero and lastRPS is greater than zero. If the claim function is called a second time after the distribution has already ended, _updateEmissions runs again and overwrites lastRPS with the now‑zero rewardsPerSecond, effectively erasing the cached rate. As a result, when new rewards are deposited, the condition lastRPS > 0 fails and rewardsPerSecond remains zero, so the reward stream never restarts. This can be triggered by any user who can invoke claim after the period has expired, causing future rewards to disappear even though tokens have been deposited. From a user’s perspective the UI will show that a deposit was made but subsequent claim attempts return zero tokens, balances stay unchanged and the expected reward accrual never occurs. The issue was uncovered during a security audit by reproducing the scenario in a unit test that called claim twice after the end time. It is subtle because lastRPS appears to be an internal cache and a zero value is not obviously erroneous, making the bug easy to miss in casual testing. The proper fix is to protect the update of lastRPS so it only occurs when rewardsPerSecond is non‑zero, or to ensure that registerRewardDeposit can recover the previous rate even if lastRPS has been cleared, thereby preserving the ability to restart reward distribution.

## Proof of Concept
When [`ChefIncentivesController#claim()`](https://github.com/code-423n4/2024-07-loopfi/blob/main/src/reward/ChefIncentivesController.sol#L518-L550) is called to vest reward for eligible user, `_updateEmissions()` is invoked first. This function checks if the current reward distribution has ended and, if so, stores the value of `rewardsPerSecond` into `lastRPS` for future use:
```solidity
function _updateEmissions() internal {
    if (block.timestamp > endRewardTime()) {
        _massUpdatePools();
        lastRPS = rewardsPerSecond;
        rewardsPerSecond = 0;
        return;
    }
    setScheduledRewardsPerSecond();
}
```
When new rewards are deposited, the cached value in `lastRPS` should be restored to `rewardsPerSecond` to restart the reward distribution.
```solidity
function registerRewardDeposit(uint256 _amount) external onlyOwner {
    depositedRewards = depositedRewards + _amount;
    _massUpdatePools();
    if (rewardsPerSecond == 0 && lastRPS > 0) {
        rewardsPerSecond = lastRPS;
    }
    emit RewardDeposit(_amount);
}
```
However, if somehow `claim()` is called twice continually when the current reward distribution ends, `lastRPS` will be set to `0` and `registerRewardDeposit()` can not restart new reward distribution.

Copy below codes to [ChefIncentivesController.t.sol](https://github.com/code-423n4/2024-07-loopfi/blob/main/src/test/unit/ChefIncentivesController.t.sol) and run `forge test --match-test test_setLastRPStoZero`:
```solidity
function test_setLastRPStoZero() public {
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    _excludeContracts(alice);
    _excludeContracts(bob);
    uint rps = incentivesController.rewardsPerSecond();
    incentivesController.addPool(address(0x1), 1000);
    incentivesController.addPool(address(0x2), 1000);
    incentivesController.setRewardsPerSecond(rps, true);
    loopToken.mint(address(incentivesController), 1000 ether);
    uint256 rewardAmount = 1000 ether;
    incentivesController.registerRewardDeposit(rewardAmount);

    incentivesController.start();

    vm.warp(block.timestamp + 30 days);

    address[] memory vaults = new address[](2);
    vaults[0] = address(0x1);
    vaults[1] = address(0x2);

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.isEligibleForRewards.selector, alice),
        abi.encode(true)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.refresh.selector, alice),
        abi.encode(true)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.getDqTime.selector, alice),
        abi.encode(0)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.isEligibleForRewards.selector, bob),
        abi.encode(true)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.refresh.selector, bob),
        abi.encode(true)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(EligibilityDataProvider.getDqTime.selector, bob),
        abi.encode(0)
    );

    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(IEligibilityDataProvider.lastEligibleStatus.selector, alice),
        abi.encode(true)
    );
    vm.mockCall(
        mockEligibilityDataProvider,
        abi.encodeWithSelector(IEligibilityDataProvider.lastEligibleStatus.selector, bob),
        abi.encode(true)
    );
    vm.prank(address(0x1));
    incentivesController.handleActionAfter(alice, 500 ether, 1000 ether);
    vm.prank(address(0x2));
    incentivesController.handleActionAfter(bob, 500 ether, 1000 ether);

    vm.warp(block.timestamp + 30 days);

    vm.mockCall(
        mockMultiFeeDistribution,
        abi.encodeWithSelector(IMultiFeeDistribution.vestTokens.selector, alice, 1000 ether),
        abi.encode(true)
    );
    vm.mockCall(
        mockMultiFeeDistribution,
        abi.encodeWithSelector(IMultiFeeDistribution.vestTokens.selector, bob, 1000 ether),
        abi.encode(true)
    );
    //@audit-info rewardsPerSecond is 1e16 before claim for alice 
    assertEq(incentivesController.lastRPS(), 0);
    assertEq(incentivesController.rewardsPerSecond(), 10000000000000000);
    incentivesController.claim(alice, vaults);
    //@audit-info rewardsPerSecond is set to 0, and its previous value is stored in lastRPS for future use
    assertEq(incentivesController.lastRPS(), 10000000000000000);
    assertEq(incentivesController.rewardsPerSecond(), 0);
    incentivesController.claim(bob, vaults);
    //@audit-info however, lastRPS is updated to 0 when claim() is called again for bob.
    assertEq(incentivesController.lastRPS(), 0);
    assertEq(incentivesController.rewardsPerSecond(), 0);
    //@audit-info new reward deposit can not restart distribution
    loopToken.mint(address(incentivesController), 1000 ether);
    incentivesController.registerRewardDeposit(1000 ether);
    assertEq(incentivesController.rewardsPerSecond(), 0);
}
```

## Recommendation
`lastRPS` should not be updated when `rewardsPerSecond` is `0`:
```solidity
function _updateEmissions() internal {
    if (block.timestamp > endRewardTime()) {
        _massUpdatePools();
        if (rewardsPerSecond != 0) {
            lastRPS = rewardsPerSecond;
        }
        rewardsPerSecond = 0;
        return;
    }
    setScheduledRewardsPerSecond();
}
```
