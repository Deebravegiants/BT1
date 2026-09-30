# [M] The fee charged on new deposits is calcu-

## Summary
Severity: Medium
Contest weight: 0.4559
Dataset id: 22927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fee charged on new deposits is calculated incorrectly. Each pool charges a fee on deposits that is redistributed to all other depositors. This is achieved by: 1. Calculating the amount of shares the depositor is supposed to receive based on the dollar value of the deposited asset 2. Minting to the depositor an amount of shares that is lower than the one they should receive, based on a fee set by the pool manager These calculations are performed in PoolLogic::_depositFor():

```solidity
...
uint256 usdAmount = IPoolManagerLogic(poolManagerLogic).assetValue(_asset, _amount);
{
    (, , uint256 entryFeeNumerator, uint256 denominator) = IPoolManagerLogic(poolManagerLogic).getFee();
    if (totalSupplyBefore > 0) {
        liquidityMinted = usdAmount.mul(totalSupplyBefore).mul(denominator.sub(entryFeeNumerator)).div(fundValue).div(denominator);
    } else {
        ...
    }
}
...
```

This is incorrect because the depositor itself will receive part of the fees he is supposed to pay, resulting in the depositor paying a lower fee than the intended one. As an example, let's assume: • usdAmount: 1000e18 • fundValue: 5000e18 • denominator: 10000 • numerator: 100 • totalSupplyBefore: 5000e18 This will result in liquidityMinted being equal to: (1000e18 × 5000e18 × (10000 − 100)) / 5000e18 / 10000 = 9.9 × 1020 shares As soon as the 9.9e20 shares are minted, their value will be: 9.9e20 × ((5000e18 + 1000e18) / (5000e18 + 9.9e20)) = 9.9165 × 1020 dollars A higher value than the expected value the depositor should receive, which is: 1000e18 × (10000 − 100) / 10000 = 9.9 × 1020 dollars The fee paid on new deposited amounts is lower than expected leading to: • Depositor paying a lower fee than expected • Users that have already deposited in the pool earning less

## Recommendation
The correct formula to determine the amount of shares to mint can be retrieved by solving the following equation for liquidityMinted:  
liquidityMinted × ((fundValue + usdAmount) / (totalSupplyBefore + liquidityMinted)) = usdAmount × (denominator − numerator) / denominator  
which results in:  
liquidityMinted = (totalSupplyBefore × usdAmount × (denominator − numerator)) / ((denominator × fundValue) + (numerator × usdAmount))
