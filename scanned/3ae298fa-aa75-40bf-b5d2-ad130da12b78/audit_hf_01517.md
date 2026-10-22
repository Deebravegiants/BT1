# [M] Fee growth inside could overflow causing a function to revert

## Summary
Severity: Medium
Contest weight: 0.4323
Dataset id: 8032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When operations need to calculate the fee growth of a Uniswap V3 position, they utilize a function similar to the one implemented in Uniswap V3. However, as noted in this known issue, the contract implicitly relies on underflow/overflow when calculating fee growth. If underflow is prevented, certain operations that depend on fee growth may revert.  
Due to the use of a different Solidity version, these calculations could revert due to overflow. Although this implementation resembles the library provided by Uniswap, it is important to note that Uniswap uses Solidity 0.6, which does not revert on overflow, whereas this contract is using Solidity 0.8.

```solidity
if (tickCurrent < tickLower) {
    feeGrowthInside0X128 = lowerFeeGrowthOutside0X128 - upperFeeGrowthOutside0X128;
    feeGrowthInside1X128 = lowerFeeGrowthOutside1X128 - upperFeeGrowthOutside1X128;
} else if (tickCurrent < tickUpper) {
    uint256 feeGrowthGlobal0X128 = pool.feeGrowthGlobal0X128();
    uint256 feeGrowthGlobal1X128 = pool.feeGrowthGlobal1X128();
    feeGrowthInside0X128 = feeGrowthGlobal0X128 - lowerFeeGrowthOutside0X128
        - upperFeeGrowthOutside0X128;
    feeGrowthInside1X128 = feeGrowthGlobal1X128 - lowerFeeGrowthOutside1X128
        - upperFeeGrowthOutside1X128;
} else {
    feeGrowthInside0X128 = upperFeeGrowthOutside0X128 - lowerFeeGrowthOutside0X128;
    feeGrowthInside1X128 = upperFeeGrowthOutside1X128 - lowerFeeGrowthOutside1X128;
}
```

## Recommendation
Consider using unchecked when calculating feeGrowthInside0X128 and feeGrowthInside1X128.  
Farms_audit.md
