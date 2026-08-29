# [M] `latestAnswer()` may return stale values

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/355
Type: code-finding

## Details
### Lines of code

--------------

[121](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L121-L121), [122](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L122-L122), [123](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L123-L123), [124](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/ARBTriCryptoOracle.sol#L124-L124), [51](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/oracle/implementations/SGOracle.sol#L51-L51)

### Vulnerability details

-------------

`latestAnswer()` only returns the latest answer or zero, and thus there is no way to tell whether the value is stale or not. Use `latestRoundData()` instead, and check whether the latest timestamp is within your protocol's limits.

```solidity
File: contracts/oracle/implementations/ARBTriCryptoOracle.sol

121:         uint256 _btcPrice = uint256(BTC_FEED.latestAnswer()) * 1e10;

122:         uint256 _wbtcPrice = uint256(WBTC_FEED.latestAnswer()) * 1e10;

123:         uint256 _ethPrice = uint256(ETH_FEED.latestAnswer()) * 1e10;

124:         uint256 _usdtPrice = uint256(USDT_FEED.latestAnswer()) * 1e10;

```



```solidity
File: contracts/oracle/implementations/SGOracle.sol

51:              uint256(UNDERLYING.latestAnswer())) / SG_POOL.totalSupply();

```


### Assessed type

------------

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/355_
