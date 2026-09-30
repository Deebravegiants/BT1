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

Even bigger problem is that, in the SpotOracle, getSpot() function will give preference to exchangeRate becoz of the Math.min function and effectively apply this rate to both reserve and spot.

.

**Attack Scenario**\

a) add three feeds to a collateral.

b) set quorum to 3

c) dont configure the collateral asset rate in two of the feeds. 

**Attachments**

1. **Proof of Concept (PoC) File**

Note how the aggregate exchange is computed without checking for exchange rate from the feed to be greater than 0.

This leads to lower exchange rate.
```
if (QUORUM == 0) {
            return type(uint256).max;
        } else if (QUORUM == 1) {
            val = FEED0.getExchangeRate(_ILK_INDEX);
        } else if (QUORUM == 2) {
            // @assuming that all feeds have exchangeRate for ild_index
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));
        } else if (QUORUM == 3) {
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            uint256 feed2ExchangeRate = FEED2.getExchangeRate(_ILK_INDEX);
            val = ((feed0ExchangeRate + feed1ExchangeRate + feed2ExchangeRate) / uint256(QUORUM));
        }
```

Refer to how the min of price from external source and exchange rate from reserver is taken. In the reserve exchange as the exchange rate could be 1/2 or 1/3 if not configured, the reserve rate will be lower than external source price and hence exchange rate take precedence due to min of the two prices as in the function below.

hence this function impacts the spot exchange rates and makes it difficult to notice and could adversely impact the users and the protocol.

```

function getSpot() external view returns (uint256 spot) {
        uint256 price = getPrice(); // must be [wad]
        uint256 exchangeRate = RESERVE_ORACLE.currentExchangeRate();

        // Min the price with reserve oracle before multiplying by ltv
        uint256 min = Math.min(price, exchangeRate); // [wad]

        spot = LTV.wadMulDown(min); 
}
```

issue functions.txt

2. **Revised Code File (Optional)**
The solution is to check the price returned for each of the feeds in the quorum and based on the valid number of prices returned, revise the aggregation logic or revert to let the owner know and configure the exchange rate across the feeds.

The second option is illustrated as below.
```
function _aggregate(uint8 _ILK_INDEX) internal view returns (uint256 val) {
        if (QUORUM == 0) {
            return type(uint256).max;
        } else if (QUORUM == 1) {
            val = FEED0.getExchangeRate(_ILK_INDEX);
            require(val > 0,"Incorrect exchange rate");
        } else if (QUORUM == 2) {
            // @assuming that all feeds have exchangeRate for ild_index
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            require(feed0ExchangeRate > 0,"Incorrect exchange rate0");
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            require(feed1ExchangeRate > 0,"Incorrect exchange rate1");
            val = ((feed0ExchangeRate + feed1ExchangeRate) / uint256(QUORUM));
        } else if (QUORUM == 3) {
            uint256 feed0ExchangeRate = FEED0.getExchangeRate(_ILK_INDEX);
            require(feed0ExchangeRate > 0,"Incorrect exchange rate0");
            uint256 feed1ExchangeRate = FEED1.getExchangeRate(_ILK_INDEX);
            require(feed1ExchangeRate > 0,"Incorrect exchange rate1");
            uint256 feed2ExchangeRate = FEED2.getExchangeRate(_ILK_INDEX);
            require(feed2ExchangeRate > 0,"Incorrect exchange rate2");
            val = ((feed0ExchangeRate + feed1ExchangeRate + feed2ExchangeRate) / uint256(QUORUM));
        }
}

```

solution2.txt
  
**Files:**
  - Issue functions.txt (https://hats-backend-prod.herokuapp.com/v1/files/QmPurhvHSVDZ9wL9Pcgvt5F9yFtu3yecyerUcSKH2TKPAZ)
  - Issue2.txt (https://hats-backend-prod.herokuapp.com/v1/files/Qma8fN8sVLyTtcHWPyaS5X4kYWNiK7DnfqwXjHHF3BvSxp)
  - solution2.txt (https://hats-backend-prod.herokuapp.com/v1/files/QmPErRVfny3dUQan1TAeThETqNrdDJrfPAZoLr1e1k3Ds9)
