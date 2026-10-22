# [M] tokenPriceAtLastFeeMint is not resetted to 1e18

## Summary
Severity: Medium
Contest weight: 0.5895
Dataset id: 22929
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The variable tokenPriceAtLastFeeMint is not resetted to 1e18 when the pool gets to a state where totalSupply() is 0, resulting in the performance fee not being distributed until currentTokenPrice becomes bigger than tokenPriceAtLastFeeMint again. The performance fee is calculated by PoolLogic::_mintManagerFee() on the profit earned by a pool since the previous performance fee distribution. The pool distributes the performance fee on every deposit and withdrawal but only when currentTokenPrice is greater than tokenPriceAtLastFeeMint (ie. the current value per share is higher than the value per share of the last performance fees distribution):

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

The variable tokenPriceAtLastFeeMint is updated by the PoolLogic::_mintManagerFee() function only when fees are distributed (ie. the currentTokenPrice is higher than tokenPriceAtLastFeeMint):

```solidity
...
uint256 currentTokenPrice = _tokenPrice(fundValue, tokenSupply);
if (tokenPriceAtLastFeeMint < currentTokenPrice) {
    tokenPriceAtLastFeeMint = currentTokenPrice;
}
...
```

If at some point during its lifetime a pool returns to a state where the totalSupply() of shares is 0 the variable tokenPriceAtLastFeeMint will keep its current value, but currentTokenPrice gets reset to a value 1:1 relative to the amount of dollars deposited. This results in the performance fee not being distributed until currentTokenPrice will be greater than tokenPriceAtLastFeeMint again. Performance fee is not distributed if a pool reaches a state where totalSupply() is 0 during its lifetime.

## Recommendation
After a withdrawal reset the tokenPriceAtLastFeeMint to 1e18 if the amount of shares of the pool is 0.
