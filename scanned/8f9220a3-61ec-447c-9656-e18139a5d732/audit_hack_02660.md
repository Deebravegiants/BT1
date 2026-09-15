# [M] Lack of price freshness check in PricerInternal.sol#_latestAnswer64x64() allows a stale price or zero price to be used

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55
Type: audit-issue

## Details
# Lack of price freshness check in PricerInternal.sol#_latestAnswer64x64() allows a stale price or zero price to be used

## Summary

PricerInternal.sol#_latestAnswer64x64() should use the updatedAt value from the latestRoundData() function to make sure that the latest answer is recent enough to be used in function _latestAnswer64x6 in PricerInternal

## Vulnerability Detail

In the current implementation of PricerInternal.sol#_latestAnswer64x64() there is no freshness check. This could lead to stale prices being used.

If the market price of the token drops very quickly ("flash crashes"), and Chainlink's feed does not get updated in time, the smart contract will continue to believe the token is worth more than the market value.

Chainlink also advise developers to check for the updatedAt before using the price:

>Your application should track the latestTimestamp variable or use the updatedAt value from the latestRoundData() function to make sure that the latest answer is recent enough for your application to use it. If your application detects that the reported answer is not updated within the heartbeat or within time limits that you determine are acceptable for your application, pause operation or switch to an alternate operation mode while identifying the cause of the delay.

And they have this heartbeat concept:

>Chainlink Price Feeds do not provide streaming data. Rather, the aggregator updates its latestAnswer when the value deviates beyond a specified threshold or when the heartbeat idle time has passed. You can find the heartbeat and deviation values for each data feed at data.chain.link or in the Contract Addresses lists.

Source: https://docs.chain.link/docs/data-feeds/#check-the-timestamp-of-the-latest-answer

## Impact

A stale price can cause the malfunction of price oracle

the function getDeltaStrikePrice64x64(), and latestAnswer64x64() can be invalid or outdated.

Thus affecting the strike price when creating or executing a option contract.

## Code Snippet

https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/pricer/PricerInternal.sol#L49-L55

## Tool used

Manual Review

## Recommendation

Consider adding the missing freshness check for stale price or zero price using round id and updatedTime

```solidity
       (
          roundId,
          rawPrice,
          ,
          updateTime,
          answeredInRound
        ) = AggregatorV3Interface(XXXXX).latestRoundData();
        require(rawPrice > 0, "Chainlink price <= 0");
        require(updateTime != 0, "Incomplete round");
        require(block.timep - updateTime < validInternvalPeriod, 'invalid price feed')
        require(answeredInRound >= roundId, "Stale price");
```
