# [M] Undercollateralized loans possible

## Summary
Severity: Medium
Contest weight: 0.3904
Dataset id: 4127
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[Comptroller.sol#L1491](https://github.com/code-423n4/2022-04-dualityfocus/blob/f21ef7708c9335ee1996142e2581cb8714a525c9/contracts/compound_rari_fork/Comptroller.sol#L1491)  

The `_setPoolCollateralFactors` function does not check that the collateral factor is < 100%.  
It’s possible that it’s set to 200% and then borrows more than the collateral is worth, stealing from the pool.

## Recommendation
Disable the possibility of ever having a collateral factor > 100% by checking:
```solidity
for (uint256 i = 0; i < pools.length; i++) {
    require(collateralFactorsMantissa[i] <= 1e18, "CF > 100%");
    poolCollateralFactors[pools[i]] = collateralFactorsMantissa[i];
}
```
We agree, we should have a max setting for collateral factor of pools to provide confidence to users. That said, this would only be abusable by admins, and so we consider low risk (since controlled by multisig).

Good catch!

Unbounded `collateralFactor` configuration made it possible for malicious/compromised privileged roles to rug the users, which I consider a real and very practical threat that should be addressed from the smart contract level.

**[0xdramaone (Duality Focus) resolved](https://github.com/code-423n4/2022-04-dualityfocus-findings/issues/12)**
