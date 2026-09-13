# [M] Oracle data misreporting can disrupt auction and options settlement

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-knox
Published: 2022-10-18
Source: https://github.com/sherlock-audit/2022-09-knox-judging/issues/103
Type: sherlock-finding

## Details
Jeiwan

medium

# Oracle data misreporting can disrupt auction and options settlement

## Summary
Know Finance allows users to buy options via Dutch auction. To start an auction round, it's required to define [the maximal and minimal prices](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L612-L628), which are calculated relatively to [the current spot price](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L580) of the underlying asset. Knowing spot price is also required to [calculate the delta strike price](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/Pricer.sol#L84), which is [set as the strike price](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L459-L461) of an option. To find spot prices, the Pricer contract [queries two Chainlink oracles](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55).  However, the returned values are not validated. Chainlink oracles can report an invalid (e.g. 0) or outdated prices.

Chainlink [recommends](https://docs.chain.link/docs/data-feeds/selecting-data-feeds/#risk-mitigation) designing systems and smart contract in a way that makes them resilient to malfunctioning of Chainlink oracles. Oracles may misreport prices in case of volatile market conditions, the degraded performance of Chainlink infrastructure, chains, or networks, and any other upstream outage related to data providers or node operators.
## Vulnerability Detail
The main cause of the issue is that the Price contract doesn't validate [prices returned by Chainlink oracles](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55).
## Impact
Let's review three potential Chainlink oracle misbehavior scenarios and how they would affect Knox Finance:
1. Base price is 0: initializing an auction or an epoch will result in a revert due to a "division by zero" error. A keeper would have to send another tx, which might get reverted again.
1. Underlying price is reported as 0.

    a. Auction initialization: [the strike price of an option](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L460-L461) will be 0 and the whole epoch will be flawed (no one will buy options because the strike price is unreachable);

    b. Epoch initialization: [the delta strike will be 0](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L572-L577), which will result in [incorrect maximal and minimal prices](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L613-L628), which will disrupt the current auction round (i.e. options buyers will be able to buy options at a wrong price).

1. Reported prices are outdated. The strike price and the maximal and minimal auction prices will be outdated. Either call options buyers or put option buyers will have an advantage depending on how the price has changes since the reported one.
## Code Snippet
```solidity
function _latestAnswer64x64() internal view returns (int128) {
    // @audit missing price and timestamp validation
    (, int256 basePrice, , , ) = BaseSpotOracle.latestRoundData();
    // @audit missing price and timestamp validation
    (, int256 underlyingPrice, , , ) =
        UnderlyingSpotOracle.latestRoundData();

    return ABDKMath64x64.divi(underlyingPrice, basePrice);
}
```
## Tool used
Manual Review

## Recommendation
In general, follow [the risk mitigation recommendations from Chainlink](https://docs.chain.link/docs/data-feeds/selecting-data-feeds/#risk-mitigation). Specifically:
> Configure your application to detect when the reported answer is close to reaching minAnswer or maxAnswer and issue an alert so you can respond to a potential market event. Separately, configure your application to detect and respond to extreme price volatility or prices that are outside of your acceptable limits.

> Your application should track the latestTimestamp variable or use the updatedAt value from the latestRoundData() function to make sure that the latest answer is recent enough for your application to use it. If your application detects that the reported answer is not updated within the heartbeat or within time limits that you determine are acceptable for your application, pause operation or switch to an alternate operation mode while identifying the cause of the delay.

Duplicate of #137
