# [M] PriceAggregator uses the same

## Summary
Severity: Medium
Contest weight: 0.2126
Dataset id: 1766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fulfill function in PriceAggregator.sol function uses the same heartbeat (chainlinkValidityPeriod) to check the freshness of the price for all the price feeds. The problem with this is different price feeds have different heartbeats. Since they use the same heartbeat the heartbeat needs to be slowest of all of them or else the staleness check will fail most of the time. The issue is that if we use slowest heartbeat of all the feeds as chainlinkValidityPeriod it would allow the consumption of potentially very stale data.
In PriceAggregator.sol:126 and PriceAggregator.sol:158 same heartbeat value chainlinkValidityPeriod is used to check the freshness of all price feeds.
Internal pre-conditions
No pre-conditions
External pre-conditions
No external pre-conditions
Attack Path
1. Lets take BTC-USD feed and EUR-USD feed as examples.
2. On Base BTC-USD chainlink feed's heartbeat is 20 minutes and EUR-USD feed's heartbeat is 24 hours.
3. So If price is not changed beyond deviation threshold they will only be updated after heartbeat period is passed.
4. If we use 20 minutes as heartbeat period to check freshness of prices staleness check will fail for EUR-USD will fail most of the times because its heartbeat is 24 hours it doesn't get updated every 20 mins.
5. If we use 24 hours as heartbeat we might consume stale BTC-USD price because the actual heartbeat of that price feed is 20 mins and chainlink sets it heartbeat to 20 mins because BTC is volatile.
6. So two different heartbeat periods should be used for validating these two price feeds.
1. Stale prices will be confirmed or
2. Price staleness check will fail most of the times.

## Recommendation
Use separate heartbeat periods for every price feed
