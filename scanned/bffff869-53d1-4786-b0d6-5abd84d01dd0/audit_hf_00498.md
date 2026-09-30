# [M] Interest will be lost if funds are

## Summary
Severity: Medium
Contest weight: 0.7355
Dataset id: 1953
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a withdraw request is made, the expected interest for the epoch is added to the withdrawal amount. This accurately predicts the owed interest when withdrawing from the senior tranche but does not accurately account for interest if the user withdrawing from the junior vault (which by default has an apr of 0).
While the interest for the individual withdrawing will be correct, the overall interest will be incorrect and well lead to loss of yield for the users in the senior tranche.
IdleCDOEpochVariant.sol#L518-L524
```solidity
uint256 interest = _calcInterestWithdrawRequest(_underlyings) * _trancheAprRatio(_tranche) / FULL_ALLOC;
uint256 fees = interest * fee / FULL_ALLOC;
uint256 netInterest = interest - fees;
// user is requesting principal + interest of next epoch minus fees
_underlyings += netInterest;
// add expected fees to pending withdraw fees counter
pendingWithdrawFees += fees;
```
We see that when calculating the interest the result is multiplied by _trancheAPRRatio which for the junior vault is 0. For normal withdrawals the funds will be lent for one additional epoch past the withdraw. These funds should be generating interest which should be given to the senior vault but no interest is generated at all. This leads to loss of yield for the senior vault as funds are effectively lent for free.
IdleCDOEpochVariant::L518 fails to properly calculate the total interest and only calculates user interest
Internal Pre-conditions
None
External Pre-conditions
None
Attack Path
1) User deposits to the junior vault
2) User later withdraws from the junior vault
Loss of yield to senior vault

## Proof of Concept
All POCs and setup at this gist. POC for this specific issue:
```solidity
function testInterestOnAATranche() public {
    vm.prank(alice);
    cdoEpoch.depositAA(100e18);
    vm.prank(alice);
    cdoEpoch.requestWithdraw(99e18, trancheAA);
    vm.prank(cdoEpoch.owner());
    cdoEpoch.startEpoch();
    underlying.mint(borrower, 100e18);
    uint256 preBalance = underlying.balanceOf(borrower);
    vm.warp(cdoEpoch.epochEndDate());
    vm.prank(cdoEpoch.owner());
    cdoEpoch.stopEpoch(11e18, 0);
    console2.log("Borrower Paid:");
    console2.log(preBalance - underlying.balanceOf(borrower));
}
```
```solidity
function testLostInterestOnBBTranche() public {
    vm.startPrank(alice);
    cdoEpoch.depositAA(1e18);
    cdoEpoch.depositBB(99e18);
    cdoEpoch.requestWithdraw(99e18, trancheBB);
    vm.stopPrank();
    vm.prank(cdoEpoch.owner());
    cdoEpoch.startEpoch();
    underlying.mint(borrower, 100e18);
    uint256 preBalance = underlying.balanceOf(borrower);
    vm.warp(cdoEpoch.epochEndDate());
    vm.prank(cdoEpoch.owner());
    cdoEpoch.stopEpoch(11e18, 0);
    console2.log("Borrower Paid:");
    console2.log(preBalance - underlying.balanceOf(borrower));
}
```
[PASS] testInterestOnAATranche() (gas: 723184)
Logs:
Borrower Paid:
99823287671232876706
[PASS] testLostInterestOnBBTranche() (gas: 810917)
Logs:
Borrower Paid:
99009589041095890410
We see that the borrower pays significantly less interest when the BB tranche is withdrawn causing loss of funds to the AA tranche.

## Recommendation
Total interest should be calculate prior. Interest owed the user should be added to _underlyings and everything else should be added to expectedEpochInterest.
