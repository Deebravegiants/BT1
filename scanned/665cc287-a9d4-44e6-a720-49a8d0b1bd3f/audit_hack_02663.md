# [M] Oracle data can be outdated

## Summary
Severity: Medium
Reporter: Trumpero
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L50-L52
Type: audit-issue

## Details
# Oracle data can be outdated

## Lines of code
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L50-L52

## Summary
The `lastRoundData()`'s parameters according to [Chainlink](https://docs.chain.link/docs/data-feeds/price-feeds/api-reference/) are the following:
```solidity=
function latestRoundData() external view
    returns (
        uint80 roundId,             //  The round ID.
        int256 answer,              //  The price.
        uint256 startedAt,          //  Timestamp of when the round started.
        uint256 updatedAt,          //  Timestamp of when the round was updated.
        uint80 answeredInRound      //  The round ID of the round in which the answer was computed.
    )
```

But function `_lastestAnswer64x64` just get the parameter `price`, and hasn't checked the others. 
```solidity=
function _latestAnswer64x64() internal view returns (int128) {
    (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
    (, int256 underlyingPrice, , , ) =
        UnderlyingSpotOracle.latestRoundData();

    return ABDKMath64x64.divi(underlyingPrice, basePrice);
}
```
It can lead to a potential risk for protocol 

## Vulnerability Detail
A strong reliance on the price feeds has to be also monitored as recommended on the [Risk Mitigation section](https://docs.chain.link/docs/data-feeds/selecting-data-feeds/#risk-mitigation). There are several reasons why a data feed may fail such as unforeseen market events, volatile market conditions, degraded performance of infrastructure, chains, or networks, upstream data providers outage, malicious activities from third parties among others.

Chainlink recommends using their data feeds along with some controls to prevent mismatches with the retrieved data. Along some recommendations, the feed can include circuit breakers (for extreme price events), contract update delays (to ensure that the injected data into the protocol is fresh enough), manual kill-switches (to cease connection in case of found bug or vulnerability in an upstream contract), monitoring (control the deviation of the data) and soak testing (of the price feeds).

The retrieved price of the `BaseSpotOracle` and `UnderlyingSpotOracle` can be outdated and used anyways as a valid data because no timestamp tolerance of the update source time is checked while storing the return parameters of `latestRoundData()` inside `_latestAnswer64x64` as recommended by Chainlink. The usage of outdated data can impact on how the Payment terminals work regarding pricing calculation and value measurement.

## Impact
Function `latestAnswer64x64` is used to get the spot price to initialize the `maxPrice64x64` and `minPrice64x64` of a new epoch 
```solidity=
// url = https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L579-L581

// fetches the spot price of the underlying
int128 spot64x64 = l.Pricer.latestAnswer64x64();

...
// calculates the auction max price using the strike price further (ITM)
int128 maxPrice64x64 =
    l.Pricer.getBlackScholesPrice64x64(
        spot64x64,
        lastOption.strike64x64,
        timeToMaturity64x64,
        l.isCall
    );


// calculates the auction min price using the offset strike price further (OTM)
int128 minPrice64x64 =
    l.Pricer.getBlackScholesPrice64x64(
        spot64x64,
        offsetStrike64x64,
        timeToMaturity64x64,
        l.isCall
    );
```
If the retrieved value of the oracle is outdated, `minPrice` and `maxPrice` will suffer from this mismatch. It will affect the `_priceCurve64x64` function and make the [validation](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/auction/AuctionInternal.sol#L500-L513) of market order wrong

## Tool used
Manual Review

## Recommendation
Follow the Chainlink's recommendation:
https://docs.chain.link/docs/data-feeds/#check-the-timestamp-of-the-latest-answer
It is recommended both to add also a tolerance that compares the updatedAt return timestamp from latestRoundData() with the current block timestamp and ensure that the priceFeed is being updated with the required frequency.
