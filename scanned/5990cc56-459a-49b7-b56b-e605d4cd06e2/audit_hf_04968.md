# [M] Perfomance fee is calculated incorrectly

## Summary
Severity: Medium
Contest weight: 0.4576
Dataset id: 22928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The performance fee is calculated incorrectly leading to the manager and the dao receiving less than expected in terms of value. The dao and the pool manager are entitled to a performance fee: a percentage of the profits realized by the pool. The fee is calculated both when users either deposit or withdraw and it's distributed immediately by minting new shares. The performance fee is calculated by the PoolLogic::_availableManagerFee() function:

```solidity
...
uint256 currentTokenPrice = _fundValue.mul(10 ** 18).div(_tokenSupply);
if (currentTokenPrice > tokenPriceAtLastFeeMint) {
    available = currentTokenPrice
        .sub(tokenPriceAtLastFeeMint)
        .mul(_tokenSupply)
        .mul(_performanceFeeNumerator)
        .div(_feeDenominator)
        .div(currentTokenPrice);
}
...
```

Let's assume: • fundValue: 2e18 • tokenSupply: 1e18 • currentTokenPrice: 2e18 • tokenPriceAtLastFeeMint: 1e18 • performanceFeeNumerator: 50 • feeDenominator: 10000 With this parameters the performance fee should be valued: (0.005 × 1e18) = 5 × 1015$  
The performance fee (in terms of shares) calculated by PoolLogic::_availableManagerFee() is:  
((2e18 − 1e18) × 1e18 × 50 / 10000) / 2e18 = 2.5 × 1015 shares  
Meaning 2.5e15 new shares will be minted. As soon as the new shares are minted they will be valued at:  
2.5e15 × (2e18 / (1e18 + 2.5e15)) ≈ 4.9875 × 1015$  
The performance fee value is 4.9875e15 $ instead of 5e15 $. The manager and the dao will receive less fees than expected, the pool depositors will earn more than expected. The fee in the example is only 0.5% but the fee can be up to 50% and this applies to every single pool for the whole life of the pool, hence high severity.

## Recommendation
This happens because new shares are minted without adding funds to the pool, in such cases the formula needs to be adjusted to take this into account. The correct formula is:  
((currentTokenPrice − tokenPriceAtLastFeeMint) × performanceFeeNumerator × tokenSupply) / ((fundValue × feeDenominator) − (performanceFeeNumerator × (currentTokenPrice − tokenPriceAtLastFeeMint)))  
which will mint:  
((2e18 − 1e18) × 50 × 1e18) / ((2e18 × 10000) − (50 × (2e18 − 1e18))) = 2.5062 × 1015 shares  
As soon as they are minted, the 2.5062e15 shares will be worth:  
2.5062e15 × (2e18 / (1e18 + 2.5062e15)) = 4.999 × 1015$  
which is the value we are expecting based on the profit, fee numerator and fee denominator.
