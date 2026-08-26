# [M] Aave price oracle can be changed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/21
Type: sherlock-finding

## Details
rvierdiiev

medium

# Aave price oracle can be changed

## Summary
Aave price oracle can be changed in `PoolAddressesProvider`, but the protocol will continue use old one as it sets it on initialization instead of fetching from `PoolAddressesProvider` every time.
## Vulnerability Detail
The protocol uses aave price oracle to get token prices. 
https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/libraries/DnGmxJuniorVaultManager.sol#L1099-L1107
```solidity
    function _getTokenPrice(State storage state, IERC20Metadata token) private view returns (uint256) {
        uint256 decimals = token.decimals();

        // AAVE oracle
        uint256 price = state.oracle.getAssetPrice(address(token));

        // @dev aave returns from same source as chainlink (which is 8 decimals)
        return price.mulDivDown(PRICE_PRECISION, 10**(decimals + 2));
    }
```
For DnGmxJuniorVault `state.oracle` value is stored in 2 methods. In [`initialize`](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L116) and in [`setHedgeParams`](https://github.com/sherlock-audit/2022-10-rage-trade/blob/main/dn-gmx-vaults/contracts/vaults/DnGmxJuniorVault.sol#L275).

In both cases oracle address is fetched using `poolAddressProvider.getPriceOracle()`. Once it's set, then oracle address is not updating and protocol using it for calculations.

But aave `PoolAddressesProvider` has a setter method to change price oracle.
https://github.com/aave/aave-v3-core/blob/master/contracts/protocol/configuration/PoolAddressesProvider.sol#L105-L109
```solidity
  function setPriceOracle(address newPriceOracle) external override onlyOwner {
    address oldPriceOracle = _addresses[PRICE_ORACLE];
    _addresses[PRICE_ORACLE] = newPriceOracle;
    emit PriceOracleUpdated(oldPriceOracle, newPriceOracle);
  }
```

That means that in any time owner of PoolAddressesProvider can change price oracle, while the protocol will continue using old oracle. This can lead to unpredictable results from simple reverting on calls or returning outdated values.
In case when prices will be incorrect, protocol will have calculations problems.

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/21_
