# [M] Exchange Rate aggregation can lead to lower pricing and opens to vulnerability for the protocol and users

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-02-03
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/46
Type: hats-finding

## Details
**Github username:** @https://github.com/betharavikiran
**Twitter username:** @ravikiranweb3
**Submission hash (on-chain):** 0x6a5274a92fc8c1e9d6abedc2e5b2ee64e13082ec5d1b16364f72d644fe719e7e
**Severity:** medium

**Description:**
**Description**\
Describe the context and the effect of the vulnerability. ReserveOracle refers to three feeds in addtion to the protocol feed for underlying asset type. The reserveFeed is manually maintained by the owner of a contract that sets the exchange rate for each collateral type for each feeds.

The reserve Oracle also has a quorum mechanism under which the the exchange from the manual feeds is aggregated based the configured quorum. Refer to the below function for how the aggregation is being done in the aggregate function.

Refer to issueFunctions.txt.

The problem happens in the above aggregate function where aggregate value is computed as below

  ` val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));`

So, for example, ETH rate from the two feeds for quorum 2 is as below 

`val = (2000 + 2002)/2 = 4002/2 = 2001`

`val = 2001`

now, let say, feed2 was not configured for ETH rate, but the quorum is still 2 in which case, the aggregate value for exchange rate will be 

` val = (2000 + 0)/2 = 1000`

So, instead of 2000 range, the value drops to half in the case of quorum two and 1/3 incase the case of quorum 3 and only 1 feed has the rate configured for the collateral.

The risk here is that, feed contract stores data in a map with exchange rates as below. 

`mapping(uint8 ilkIndex => uint256 exchangeRate) public exchangeRates;`

**Since the map for all collaterals will default to 0, this is a silent error.**

hence, **the rate is default to 0** and that have huge implications in the protocol. This is a silent error that will not be noticed as it starts from inititalization of rates and will stay there. The _maxChange guard also does not offer protection.

**Impact on spot exchange rate:**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/46_
