# [M] Integer underflow if a token specifies more than 18 decimals

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Decimals are provided by the account deploying the price provider contract. In `getEthBalanceByToken` the assumption is made that `decimals[index]` is less or equal to `18` decimals, however, the deployer may provide decimals that are not within normal operating bounds. Contract creation succeeds, while the contract is not viable.

#### Examples

The value underflows if the contract is used with a token decimals > 18.

###### Balancer


**code/aave-balancer-3e8367ab/contracts/proxies/BalancerSharedPoolPriceProvider.sol:L69-L78**
```solidity
function getEthBalanceByToken(uint256 index)
    internal
    view
    returns (uint256)
{
    uint256 pi = isPeggedToEth[index]
        ? BONE
        : uint256(priceOracle.getAssetPrice(tokens[index]));
    require(pi > 0, "ERR_NO_ORACLE_PRICE");
    uint256 missingDecimals = 18 - decimals[index];
```

##### Uniswapv2


**code/aave-uniswapv2-e81cf872/contracts/proxies/UniswapV2PriceProvider.sol:L57-L66**
```solidity
function getEthBalanceByToken(uint256 index, uint112 reserve)
    internal
    view
    returns (uint256)
{
    uint256 pi = isPeggedToEth[index]
        ? Math.BONE
        : uint256(priceOracle.getAssetPrice(tokens[index]));
    require(pi > 0, "ERR_NO_ORACLE_PRICE");
    uint256 missingDecimals = 18 - decimals[index];
```

#### Recommendation

Add a check to the constructor to ensure that none of the provided decimals is greater than 18.
