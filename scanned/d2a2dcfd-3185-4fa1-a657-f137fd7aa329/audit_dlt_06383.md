# [M] `WiseOracleHub.getTokensPriceInUSD` function uses the returned ETH price without validation

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-15
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/29
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xd932d4999df7e0fe1e50b62447d2343df0fd6d557c2c4396bd4819c1d173a26a
**Severity:** medium

**Description:**
## Description

- `WiseOracleHub.getTokensPriceInUSD` function is designed to return the USD value of a token:

  ```javascript
      function getTokensPriceInUSD(
          address _tokenAddress,
          uint256 _tokenAmount
      )
          external
          view
          returns (uint256)
      {
          return getTokensInETH(
              _tokenAddress,
              _tokenAmount
          )
              * getETHPriceInUSD()
              / 10 ** _decimalsUSD;
      }
  ```

  - first, it fetches the token/ETH value from a chainlink pricefeed,
  - then it extracts the ETH USD price via `getETHPriceInUSD`,
  - the token USD price will be the multiplication of the above fetched values.

- [`getETHPriceInUSD`](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/WiseOracleHub/OracleHelper.sol#L121C5-L136C6) uses `Chainlink.latestRoundData()` to fetch ETH price data, where this call will [return](https://docs.chain.link/data-feeds/api-reference#latestrounddata):

```javascript
function latestRoundData() external view
    returns (
        uint80 roundId,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/29_
