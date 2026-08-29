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


_Trimmed to 38 lines — full report: https://github.com/hats-finance/Wise-Lending-0xa2ca45d6e249641e595d50d1d9c69c9e3cd22573/issues/1_
