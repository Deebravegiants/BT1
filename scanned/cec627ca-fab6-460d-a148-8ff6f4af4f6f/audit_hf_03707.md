# [H] Fee receiver is given twice the amount of bor-

## Summary
Severity: High
Contest weight: 0.6525
Dataset id: 19815
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fee receiver is given twice the amount of borrow fees it's owed, at the expense of the user's position.
The calculation of the total net cost of a position change double counts the portion of the fee related to how much the fee receiver gets of the fee of the borrowed amount.
The fee receiver gets twice the amount owed, and the user is charged twice what they should be for that portion of their order.
borrowingFeeAmount contains both the amount for the pool and the amount for the fee receiver. The totalNetCostAmount calculation includes the full borrowingFeeAmount even though the feeReceiverAmount is also included, and already contains the borrowingFeeAmountForFeeReceiver.
```solidity
// File: gmx-synthetics/contracts/pricing/PositionPricingUtils.sol :
PositionPricingUtils.getPositionFees()
#1
fees.borrowingFeeAmount = MarketUtils.getBorrowingFees(dataStore, position) / collateralTokenPrice.min;
uint256 borrowingFeeReceiverFactor = dataStore.getUint(Keys.BORROWING_FEE_RECEIVER_FACTOR);
uint256 borrowingFeeAmountForFeeReceiver = Precision.applyFactor(fees.borrowingFeeAmount, borrowingFeeReceiverFactor);
fees.feeAmountForPool = fees.positionFeeAmountForPool + fees.borrowingFeeAmount - borrowingFeeAmountForFeeReceiver;
fees.feeReceiverAmount += borrowingFeeAmountForFeeReceiver;
int256 latestLongTokenFundingAmountPerSize = MarketUtils.getFundingAmountPerSize(dataStore, position.market(), longToken, position.isLong());
int256 latestShortTokenFundingAmountPerSize = MarketUtils.getFundingAmountPerSize(dataStore, position.market(), shortToken, position.isLong());
fees.funding = getFundingFees(
    position,
    longToken,
    shortToken,
    latestLongTokenFundingAmountPerSize,
    latestShortTokenFundingAmountPerSize
);
fees.totalNetCostAmount = fees.referral.affiliateRewardAmount + fees.feeReceiverAmount + fees.positionFeeAmountForPool + fees.funding.fundingFeeAmount + fees.borrowingFeeAmount;
fees.totalNetCostUsd = fees.totalNetCostAmount * collateralTokenPrice.max;
return fees;
cts/pricing/PositionPricingUtils.sol#L377-L400
```

## Recommendation
```diff
diff --git a/gmx-synthetics/contracts/pricing/PositionPricingUtils.sol b/gmx-synthetics/contracts/pricing/PositionPricingUtils.sol
index c274e48..30bd6a8 100644
--- a/gmx-synthetics/contracts/pricing/PositionPricingUtils.sol
+++ b/gmx-synthetics/contracts/pricing/PositionPricingUtils.sol
@@ -393,7 +393,7 @@ library PositionPricingUtils {
     latestShortTokenFundingAmountPerSize
 );
- fees.totalNetCostAmount = fees.referral.affiliateRewardAmount + fees.feeReceiverAmount + fees.positionFeeAmountForPool + fees.funding.fundingFeeAmount + fees.borrowingFeeAmount;
+ fees.totalNetCostAmount = fees.referral.affiliateRewardAmount + fees.feeReceiverAmount + fees.feeAmountForPool + fees.funding.fundingFeeAmount;
 fees.totalNetCostUsd = fees.totalNetCostAmount * collateralTokenPrice.max;
 return fees;
```
