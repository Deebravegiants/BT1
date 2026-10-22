# [M] Unchecked Specification requirement - token limit

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

According to the `Balancer Shared Pool Price Provider` that was provided with the audit code-base the price provide must fulfill the following requirements:

>  - Pool token price cannot be manipulated
>  - Chainlink will be used as the main oracle
>  - It should use as less gas as possible
>  - Limited to Balancer’s shared pools where the weights cannot be changed
>  - Limited to a pool containing 2 to 3 tokens

However, the constructor of the price provider does not enforce the limit of 2 to 3 tokens.

#### Examples


**code/aave-balancer-3e8367ab/contracts/proxies/BalancerSharedPoolPriceProvider.sol:L38-L63**
```solidity
constructor(
    BPool _pool,
    bool[] memory _isPeggedToEth,
    uint8[] memory _decimals,
    IPriceOracle _priceOracle,
    uint256 _priceDeviation,
    uint256 _K,
    uint256 _powerPrecision,
    uint256[][] memory _approximationMatrix
) public {
    pool = _pool;
    //Get token list
    tokens = pool.getFinalTokens(); //This already checks for pool finalized
    //Get token normalized weights
    uint256 length = tokens.length;
    for (uint8 i = 0; i < length; i++) {
        weights.push(pool.getNormalizedWeight(tokens[i]));
    }
    isPeggedToEth = _isPeggedToEth;
    decimals = _decimals;
    priceOracle = _priceOracle;
    priceDeviation = _priceDeviation;
    K = _K;
    powerPrecision = _powerPrecision;
    approximationMatrix = _approximationMatrix;
}
```

#### Recommendation

Require that the number of tokens returned by `pool.getFinalTokens()` is `2<= len <=3`.
