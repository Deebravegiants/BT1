# [M] Potential Manipulation of BToken Prices

## Summary
Severity: Medium
Contest weight: 0.4546
Dataset id: 11903
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Deri-V2 protocol, each base token has a price oracle that is based on the widely used UniswapV2 time-weighted average price (TWAP). The TWAP is constructed by reading the cumulative price from a UniswapV2 pair at the beginning and at the end of the desired interval. The diﬀerence in this cumulative price can then be divided by the length of the interval to create a TWAP for that period. To elaborate, we show below the getPrice() implementation. It comes to our attention that the interval used to compute the TWAP is not restricted (line 58). As a result, it leaves the room or possibility for undesired price manipulation. To mitigate, it is helpful to ensure a minimum interval for the TWAP-based price calculation.

```solidity
function getPrice() public override returns (uint256) {
    IUniswapV2Pair p = IUniswapV2Pair(pair);
    uint256 reserveQ;
    uint256 reserveB;
    uint256 timestamp;
    if (isQuoteToken0) {
        (reserveQ, reserveB, timestamp) = p.getReserves();
    } else {
        (reserveB, reserveQ, timestamp) = p.getReserves();
    }
    if (timestamp != timestampLast2) {
        priceCumulativeLast1 = priceCumulativeLast2;
        timestampLast1 = timestampLast2;
        priceCumulativeLast2 = isQuoteToken0 ? p.price0CumulativeLast() : p.price1CumulativeLast();
        timestampLast2 = timestamp;
    }
    uint256 price;
    if (timestampLast1 != 0) {
        // TWAP
        price = (priceCumulativeLast2 - priceCumulativeLast1) * 10**(18 + qDecimals - bDecimals) / (timestampLast2 - timestampLast1);
    } else {
        // Spot
        // this price will only be used when BToken is newly added to pool
        // since the liquidity for newly added BToken is always zero,
        // there will be no manipulation consequences for this price
        price = reserveB * 10**(18 + qDecimals - bDecimals) / reserveQ;
    }
    Public return price;
}
```

## Recommendation
Develop an eﬀective mitigation to avoid the price oracle from being manipulated.
