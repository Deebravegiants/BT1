# [M] Poor validation or prices

## Summary
Severity: Medium
Reporter: Chain-
Contest weight: 0.4713
Dataset id: 19690
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GMXAdapter contract integrates with Chainlink feeds, however prices reported by Chainlink feeds are not thoroughly validated. This exposes the protocol to the negative impact of extreme market events, possible malicious activity of Chainlink data feeders or its contracts, potential delays, and outages.
The _getChainlinkPrice function of GMXAdapter reads a price from a Chainlink feed and ignores the updatedAt value returned by latestRoundData (GMXAdapter.sol#L192):
```solidity
(, int answer, , , ) = assetPriceFeed.latestRoundData();
if (answer <= 0) {
    revert InvalidAnswer(address(this), answer);
}
```
Besides the answer, latestRoundData also returns updatedAt, the timestamp of when the round was updated. Chainlink Price Feeds do not provide streaming data. Rather, the aggregator updates its latestAnswer when the value deviates beyond a specified threshold or when the heartbeat idle time has passed. Due to outages or malicious activity of Chainlink data feeders, prices may be delayed or even become stale.
latestRoundData also returns roundID and answeredInRound values, which can be used to check for price reporting round completeness. However, the values are ignored and not validated, which exposes the protocol to any Chainlink issues with completing price reporting rounds.
Also, the answer is not checked against reasonable price limits: while there's a check for a zero or negative price, an invalid price may still be above zero.
By not checking the updatedAt value, GMXAdapter becomes exposed to outages in Chainlink or malicious activity of its data feeders, which may lead to incorrect pricing during liquidations or any other activity that uses the PriceType.REFERENCE price type.
In case a Chainlink price feed has failed to finalize a round, GMXAdapter won't detect a stale or an invalid price, which will affect all operations that use the reference price type.
In case a price that's outside of the reasonable limits of an asset is reported (due to an outage in Chainlink or malicious activity), GMXAdapter will fail to detect such price. As a result, any operation that uses the reference price type will be impaired.

## Recommendation
Consider following the Monitoring data feeds recommendations from Chainlink and:
1. start checking the updatedAt value returned by latestRoundData: ensure it doesn't fall outside of the heartbeat period of the price feed;
2. start checking the roundID and answeredInRound values: ensure answeredInRound is always greater or equal to roundID (See for more details);
3. start reading the maxAnswer and minAnswer from the Chainlink aggregator and ensure that prices reported by latestRoundData are always within the reasonable limit;
4. however, be aware that the maxAnswer and minAnswer values are not immutable and they may change when the Chainlink aggregator is changed.
