# [M] Lender can take borrower's collateral before

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 19935
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
For PaymentCycleType.Seconds if PaymentDefault < PaymentCycle, Lender can
take Borrower's collateral before first payment is due. If PaymentDefault > 0 but
very small, Lender can do this almost immediately after accepting borrower's bid.
This is especially bad as the Market Operator who controls these parameters can
also be the Lender.
Lender calls CollateralManager.withdraw() L254, which calls
TellerV2.isLoanDefaulted() L930, which bypasses the 1 day grace period & doesn't
take into account when first payment is due.
Borrower loses their collateral before they can even make their first repayment,
almost instantly if PaymentDefault > 0 but very small.
Put this test in TellerV2_Test.sol:
function test_LenderQuicklyTakesCollateral() public {
MarketRegistry mReg =
(MarketRegistry)(payable(address(tellerV2.marketRegistry())));
// payment cycle 3600 seconds, payment default 1 second
// payment will be in default almost immediately upon being
// accepted, even though the first payment is not due for much longer
// than the default time
uint32 PAYMENT_CYCLE_SEC
= 3600;
uint32 PAYMENT_DEFAULT_SEC = 1;
vm.startPrank(address(marketOwner));
mReg.setPaymentCycle(marketId1, PaymentCycleType.Seconds, PAYMENT_CYCLE_SEC);
mReg.setPaymentDefaultDuration(marketId1, PAYMENT_DEFAULT_SEC);
vm.stopPrank();
//Submit bid as borrower
uint256 bidId = submitCollateralBid();
// Accept bid as lender
acceptBid(bidId);
// almost immediately take the collateral as the lender, even though
// the first payment wasn't due for much later
ICollateralManager cMgr = tellerV2.collateralManager();
skip(PAYMENT_DEFAULT_SEC+1);
cMgr.withdraw(bidId);
// try again to verify the collateral has been taken
vm.expectRevert("No collateral balance for asset");
cMgr.withdraw(bidId);
}
```

## Recommendation
```solidity
Change the calculations done as a consequence of calling
TellerV2.isLoanDefaulted() to take into account when first payment is due; see
similar code which does this TellerV2.calculateNextDueDate() L886-L899. Lender
should only be able to take Borrower's collateral after the Borrower has missed
their first payment deadline by PaymentDefault seconds.
Consider enforcing sensible minimums for PaymentDefault. If PaymentDefault = 0
no liquidations will ever be possible as TellerV2._canLiquidateLoan() L963 will
always return false, so perhaps it shouldn't be possible to set PaymentDefault = 0.
```
