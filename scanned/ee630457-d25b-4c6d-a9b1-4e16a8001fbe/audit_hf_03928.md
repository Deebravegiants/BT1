# [M] price is calculated wrongly in BoundedStep-

## Summary
Severity: Medium
Contest weight: 0.5412
Dataset id: 20240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BoundedStepwiseExponentialPriceAdapter contract is trying to implement price change as scalingFactor * (e^x - 1) but the code implements scalingFactor * e^x - 1. Since there are no brackets, multiplication would be members. The getPrice code has been simplified as the following when boundary/edge cases are ignored
```solidity
(
    uint256 initialPrice,
    uint256 scalingFactor,
    uint256 timeCoefficient,
    uint256 bucketSize,
    bool isDecreasing,
    uint256 maxPrice,
    uint256 minPrice
) = getDecodedData(_priceAdapterConfigData);
uint256 timeBucket = _timeElapsed / bucketSize;
int256 expArgument = int256(timeCoefficient * timeBucket);
uint256 priceChange = scalingFactor * expExpression - WAD;
```
When timeBucket is 0, we want priceChange to be 0, so that the returned price would be the initial price. Since e^0 = 1, we need to subtract 1 (in WAD) from the expExpression. However, with the incorrect implementation, the returned price would be different than real price by a value equal to scalingFactor - 1. The image below shows the difference between the right and wrong formula when initialPrice is 100 and scalingFactor is 11. The right formula starts at 100 while the wrong one starts at 110=100+11-1 Incorrect price is returned from BoundedStepwiseExponentialPriceAdapter and that will have devastating effects on rebalance.

## Proof of Concept
• A manager wants to switch stablecoins. He wants to buy DAI and Sell USDT at a price of minimum and initial price of 1 and increasing to 1.05. • Technically, the price is not 1, but rather 1e-12 because of decimals 1e6/1e18 (1e6 in WAD) With the right formula • If he uses the scalingFactor of 2, the priceChange at t0 would be 0 • Therefore bidder would have to pay 1e18 DAI for 1e6USDT. With the wrong formula • If he uses the scalingFactor of 2, the priceChange at t0 would 1 (1e18 in WAD) instead of 0 • Therefore the price would increase by a magnitude 1e12. • Therefore, bidder would pay approximately 1e18 DAI for 1e6 * 1e12 USDT. • Attacker could take 1e12 (1 trillion USDT) with one DAI in a flash. • Or if there's not enough liquidity e.g if there's only 1m USDT, then he'll pay 1e-12 DAI. That's less than a penny. bizzyvinci My bad, I agree with Med cause the catastrophe is bounded by min and max value. pblivin0x My bad, I agree with Med cause the catastrophe is bounded by min and max value. I think we all agree this should be de-escalated to a Medium hrishibhat Result: Medium Has duplicates Considering this a valid medium based on the Escalations have been resolved successfully! Escalation status: • IAm0x52: accepted pblivin0x The remediation for this issue is open for review here https://github.com/IndexCoop/index-protocol/pull/25 The fix to the formula is here: https://github.com/IndexCoop/index-protocol/blob/839a6c699cc9217c8ee9f3b67418c64e80f0e10d/contracts/protocol/integration/auction-price/BoundedStepwiseExponentialPriceAdapter.sol#L73 IAm0x52 Fix looks good. scalingFactor is now applied via wadMul which fixes this order of operation issue.

## Recommendation
```diff
- uint256 priceChange = scalingFactor * expExpression - WAD;
+ uint256 priceChange = scalingFactor * (expExpression - WAD);
```
