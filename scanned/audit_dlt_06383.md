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
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    )
```

- where:

  - `roundId`: The round ID.
  - `answer`: The data that this specific feed provides. Depending on the feed you selected, this answer provides asset prices, reserves, NFT floor prices, and other types of data.
  - `startedAt`: Timestamp of when the round started.
  - `updatedAt`: Timestamp of when the round was updated.
  - `answeredInRound`: Deprecated - Previously used when answers could take multiple rounds to be computed.

- These returned values must be checked to verify that the returned price is fresh and not stale as this call might return stale/outdated asset price; such as checking that the returned `updatedAt` doesn't exceed a maximum delay specified by the protocol.

- But it was noticed that the price of ETH returned from [`getETHPriceInUSD`](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/WiseOracleHub/OracleHelper.sol#L121C5-L136C6) is not checked or validated anywhere, and directly used to extract the token USD price:

  ```javascript
  function getETHPriceInUSD()
          public
          view
          returns (uint256)
      {
          (
              ,
              int256 answer,
              ,
              ,
          ) = ETH_PRICE_FEED.latestRoundData();

          return uint256(
              answer
          );
      }
  ```

- Similar issue in `WiseOracleHub.getTokensPriceFromUSD`, where ut uses the returned price from `getETHPriceInUSD()` directly without validation.

## Impact

Not checking the validity of the returned ETH price will result in using an invalid price and bricking the accounting in the protocol by returning an invalid token USD price.

## Code Instance

[WiseOracleHub.getTokensPriceInUSD function](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/WiseOracleHub/WiseOracleHub.sol#L161C1-L175C6)

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

[OracleHelper.getETHPriceInUSD function](https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/blob/23e90440820fce1b355b771df0e82d4564b7fcab/contracts/WiseOracleHub/OracleHelper.sol#L121C5-L136C6)

```javascript
function getETHPriceInUSD()
        public
        view
        returns (uint256)
    {
        (
            ,
            int256 answer,
            ,
            ,
        ) = ETH_PRICE_FEED.latestRoundData();

        return uint256(
            answer
        );
    }
```

## Tool used

Manual Review

## Recommendation

Update `OracleHelper.getETHPriceInUSD` function to validate the returned price feed data in a similar way used in `OracleHelper._chainLinkIsDead` (checking the sequence if in Arbitrum, the freshness, staleness and deviation of the returned price).
