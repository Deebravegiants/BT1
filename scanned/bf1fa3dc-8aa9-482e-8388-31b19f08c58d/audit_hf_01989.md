# [M] TCR is overestimated on redemptions

## Summary
Severity: Medium
Contest weight: 0.4168
Dataset id: 11157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The system uses different price types (lowest, highest, and weighted average) depending on the nature of the operation. As such, in some operations, the most conservative price from the point of view of the protocol safety is used. For example, using the lowest price for debt creation makes sure that the amount of debt created is not higher than it should be. In the same way, using the highest price for redemptions makes sure that the amount of collateral withdrawn from the protocol is not higher than it should be. However, on redeemCollateral this same price is also used to check if the TCR is above the MCR. So using the highest price can overestimate the TCR and, consequently, allow redemptions when the real TCR is below the MCR.  
File: PositionManager.sol  
```solidity
@> (
    totals.price,
    totals.suggestedAdditiveFeePCT
) = priceFeed.fetchHighestPriceWithFeeSuggestion(
    totals.loadIncrease,
    totals.utilizationPCT,
    true,
    true
);
_requireValidMaxFeePercentage(totals.maxFeePCT, totals.suggestedAdditiveFeePCT);
uint MCR = collateralController.getMCR(address(collateralToken), totals.version);
@> _requireTCRoverMCR(totals.price, MCR);
```

## Recommendation
Use the lowest or weighted average price to calculate the TCR.
