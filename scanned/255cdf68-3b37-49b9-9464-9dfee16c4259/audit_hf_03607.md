# [M] LendingTerm.sol `_partialRepay`

## Summary
Severity: Medium
Contest weight: 0.8688
Dataset id: 19611
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user is allowed to partial repay a loan via the `_partialRepay()` function. It has a `debtToRepay` parameter which determines how much of the loan debt will be repaid. The `debtToRepay` amount should repay part of the borrowed amount and also a part of the fees and interest.

`interestRepaid` is calculated when from `debtToRepay` is subtracted the `principalRepaid`. It is made like that because we assume when we subtract the `principalRepaid` from the `debtToRepay`, the remaining amount from the `debtToRepay` is the interest.
```solidity
uint256 interestRepaid = debtToRepay - principalRepaid;
```
So far so good, but there is one require or more specifically the `interestRepaid != 0` part of the require that causes a problem:
```solidity
require(principalRepaid != 0 && interestRepaid != 0, "LendingTerm: repay too small");
```
That check is used to ensure that the amount the user is repaying is not too small; however, the `interestRepaid` would be `0` when there is `0` amount interest. A loan can be configured with `0` interest so it is a possible case. We can see it is not a problem to repay it through `_repay()` but it is impossible to partial repay it.

## Proof of Concept
Paste the following test inside `test/unit/loan/LendingTerm.t.sol`:
```solidity
function testPartialRepayWithZeroInterestFail() public {
    LendingTerm term2 = LendingTerm(
        Clones.clone(address(new LendingTerm()))
    );
    term2.initialize(
        address(core),
        term.getReferences(),
        LendingTerm.LendingTermParams({
            collateralToken: address(collateral),
            maxDebtPerCollateralToken: _CREDIT_PER_COLLATERAL_TOKEN,
            interestRate: 0,
            maxDelayBetweenPartialRepay: _MAX_DELAY_BETWEEN_PARTIAL_REPAY,
            minPartialRepayPercent: _MIN_PARTIAL_REPAY_PERCENT,
            openingFee: 0,
            hardCap: _HARDCAP
        })
    );
    vm.label(address(term2), "term2");
    guild.addGauge(1, address(term2));
    guild.decrementGauge(address(term), _HARDCAP);
    guild.incrementGauge(address(term2), _HARDCAP);
    vm.startPrank(governor);
    core.grantRole(CoreRoles.RATE_LIMITED_CREDIT_MINTER, address(term2));
    core.grantRole(CoreRoles.GAUGE_PNL_NOTIFIER, address(term2));
    vm.stopPrank();

    // prepare & borrow
    uint256 borrowAmount = 20_000e18;
    uint256 collateralAmount = 12e18;
    collateral.mint(address(this), collateralAmount);
    collateral.approve(address(term2), collateralAmount);
    bytes32 loanId = term2.borrow(borrowAmount, collateralAmount);
    assertEq(term2.getLoan(loanId).collateralAmount, collateralAmount);

    vm.warp(block.timestamp + 10);
    vm.roll(block.number + 1);
    
    // check that the loan amount is the same as the initial borrow amount to ensure there are no accumulated interest
    assertEq(term2.getLoanDebt(loanId), 20_000e18);

    credit.mint(address(this), 10_000e18);
    credit.approve(address(term2), 10_000e18);

    vm.expectRevert("LendingTerm: repay too small");
    term2.partialRepay(loanId, 10_000e18);
}
```

## Recommendation
A possible solution would be to remove the `interestRepaid != 0` from the require in `_partialRepay()`:
```solidity
-       require(principalRepaid != 0 && interestRepaid != 0, LendingTerm: repay too small");
+       require(principalRepaid != 0, LendingTerm: repay too small");
```
And a check to confirm the interest is not `0` before transferring it:
```solidity
-        CreditToken(refs.creditToken).transfer(
-            refs.profitManager,
-            interestRepaid
-        );
-
-        ProfitManager(refs.profitManager).notifyPnL(
-            address(this),
-            int256(interestRepaid)
-        );

+       if (interest != 0) {
+           CreditToken(refs.creditToken).transfer(
+               refs.profitManager,
+               interestRepaid
+           );
+
+           ProfitManager(refs.profitManager).notifyPnL(
+               address(this),
+               int256(interestRepaid)
+           );
+      }
```

I chose this to be the primary issue since it has a very high quality; including clear and insightful context, PoC, and recommendations.
