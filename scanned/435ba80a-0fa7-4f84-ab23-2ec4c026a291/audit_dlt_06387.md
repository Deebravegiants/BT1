# [M] Oracle vulnerability when the price of an underlying asset drops significantly

## Summary
Severity: Medium
Chain: Smart contract
Component: Wise-Lending
Published: 2024-02-08
Source: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/1
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xe0e09f38d16ea0e9202aa62cbca677b33fc61b61006f79b3ea7c1f674c4a312c
**Severity:** medium

**Description:**
## Impact
Oracle feed / hub will report inaccurate price during a crash. Borrowing against an inflated price asset (at chainlink's `minPrice`) can lead to significant accumulation of bad debt.

## Description
Chainlink feeds use underlying aggregators. Chainlink aggregators have a built in mechanism that prevents the price going outside of a predefined price range. During significant price drops, the oracle will continue to report the minimum price instead of the actual asset price. This would allow users to borrow against the asset at an inflated price.

If the asset's price falls below the `minPrice` threshold, the protocol will continue to value the token at `minPrice` instead of the market value. This would enable users to accumulate substantial amounts of bad debt, potentially leading to the protocol's bankruptcy. 

`CRV / USD Chainlink Feed` - [`Etherscan`](https://etherscan.io/address/0xcd627aa160a6fa45eb793d19ef54f5062f20f33f#code)
```solidity
  function latestRoundData()
    public
    view
    virtual
    override
    returns (
      uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound
    )
  {
    Phase memory current = currentPhase;

    (
      uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 ansIn
    ) = current.aggregator.latestRoundData(); // @audit uses underlying aggregator

    return addPhaseIds(roundId, answer, startedAt, updatedAt, ansIn, current.id);
  }
```

### TWAP's inablity to defend
The price difference check will pass when the `TWAP` is near the `minPrice` during a crash. A `TWAP` oracle can't really defend against this scenario, nor potentially comparing with a third oracle. Once the Uniswap oracle reports the underlying asset's value at zero, `latestResolver()` will skip the price difference comparison, simply returning the `minPrice` from `Chainlink`.

### `latestResolver()`
The first check `chainLinkIsDead()` will pass since everything works as intended (heartbeat and update time up to date). If there is a uniswap TWAP defined, it will compare the price difference with Chainlink, however during the price drop there's a short to medium timeframe when the TWAP price will be close to `minPrice`. If an asset's value drops to zero according to uniswap oracle, the difference check is skipped, as is when a TWAP oracle is not defined for `tokenAddress`.

`contracts/WiseOracleHub/WiseOracleHub.sol` - [`latestResolver()`](https://github.com/wise-foundation/lending-audit/blob/master/contracts/WiseOracleHub/WiseOracleHub.sol#L50-L90)
```solidity
    function latestResolver(
        address _tokenAddress
    )
        public
        view
        returns (uint256)
    {
        if (chainLinkIsDead(_tokenAddress) == true) {
            revert OracleIsDead();
        }

        UniTwapPoolInfo memory uniTwapPoolInfoStruct = uniTwapPoolInfo[
            _tokenAddress
        ];

        uint256 fetchTwapValue;

        if (uniTwapPoolInfoStruct.oracle > ZERO_ADDRESS) {
            fetchTwapValue = latestResolverTwap(
                _tokenAddress
            );
        }

        uint256 answer = _getChainlinkAnswer(
            _tokenAddress
        );

        if (fetchTwapValue > 0) {

            uint256 relativeDifference = _getRelativeDifference(
                answer,
                fetchTwapValue
            );

            _compareDifference(
                relativeDifference
            );
        }

        return answer;
    }
```

## Recommendation
Consider to compare `minPrice` and optionally `maxPrice` of the underlying aggregators against Chainlink's returned `answer`  from `latestResolver()` and revert the call if it's outside or equals the bounds.
```solidity
        uint256 answer = _getChainlinkAnswer(
            _tokenAddress
        );
+       if (answer >= maxPrice || answer <= minPrice) revert PriceOutOfBounds()
```

You can get the `minPrice` and `maxPrice` of the aggregator by calling `.aggregator().minPrice()` on top of the price feed. [`Aggregator`](https://etherscan.io/address/0xb4c4a493AB6356497713A78FFA6c60FB53517c63#readContract)



## Real world exploits
[Rekt - Venus Finance](https://rekt.news/venus-blizz-rekt/)
