# [M] _ineligible() redemptionEligible is miscalcu-

## Summary
Severity: Medium
Contest weight: 0.4283
Dataset id: 23193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Vault._ineligible() should not include the depositAssets of update() when calculating the redemptionEligible, which is not part of the totalCollateral.
in Vault.sol:L411
The method _ineligible() internally calculates the redemptionEligible first. using the formula: redemptionEligible = totalCollateral - (global.assets + withdrawal) - global.deposit
The problem is subtracting global.deposit, which already contains the current depositAssets. The current depositAssets is not in totalCollateral and should not be subtracted.
the redemptionEligible is too small, which causes the ineligible to be too small.
Example: context.totalCollateral = 100 , global.assets = 0, global.deposit =0
1. user call update(depositAssets = 10)
2. global.deposit += depositAssets = 10 (includes this deposit)
3. redemptionEligible = 100 - (0 + 0) - 10 = 90
The correct value should be: redemptionEligible = 100
Internal pre-conditions
External pre-conditions
Attack Path
One of the main effects of _ineligible() is that this part cannot be used as an asset to open a position; if this value is too small, too many positions are opened, resulting in the inability to claimAssets properly.

## Recommendation
```solidity
// assets eligible for redemption
// assets pending claim (use latest global assets before withdrawal for redeemability)
.unsafeSub(context.global.assets.add(withdrawal))
// assets pending deposit
.unsafeSub(context.global.deposit.sub(deposit));
return redemptionEligible
// approximate assets up for redemption
.mul(context.global.redemption.unsafeDiv(context.global.shares.add(context.global.redemption)))
// assets pending claim (use new global assets after withdrawal for eligability)
.add(context.global.assets);
// assets pending deposit are eligible for allocation
}
```
