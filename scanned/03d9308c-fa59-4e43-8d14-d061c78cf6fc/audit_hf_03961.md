# [H] Inflated price due to unnecessary precision

## Summary
Severity: High
Contest weight: 0.6426
Dataset id: 20313
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price at Line 137 below is denominated in 18 decimals as the getPriceInEth
function always returns the price in 18 decimals precision.
There is no need to scale the accumulated price by 1e18.
• It will cause the average price (existing._initAcc) to be inflated significantly
• The numerator will almost always be larger than the denominator (INIT_SAMPLE_COUNT = 18). There is no risk of it rounding to zero, so any scaling is unnecessary.
Assume that throughout the initialization process, the getPriceInEth(XYZ) always returns 2 ETH (2e18). After 18 rounds (INIT_SAMPLE_COUNT == 18) of initialization, existing._initAcc will equal 36 ETH (36e18). As such, the averagePrice will be as follows:
averagePrice = existing._initAcc * 1e18 / INIT_SAMPLE_COUNT;
averagePrice = 36e18 * 1e18 / 18
averagePrice = 36e36 / 18
averagePrice = 2e36
existing.fastFilterPrice and existing.slowFilterPrice will be set to 2e36 at Lines 157 and 158 below.
In the post-init phase, the getPriceInEth function return 3 ETH (3e18). Thus, the following code will be executed at Line 144s and 155 below:
existing.slowFilterPrice = Stats.getFilteredValue(SLOW_ALPHA, existing.slowFilterPrice, price);
existing.fastFilterPrice = Stats.getFilteredValue(FAST_ALPHA, existing.fastFilterPrice, price);
existing.slowFilterPrice = Stats.getFilteredValue(SLOW_ALPHA, 2e36, 3e18); // SLOW_ALPHA = 645e14; // 0.0645
existing.fastFilterPrice = Stats.getFilteredValue(FAST_ALPHA, 2e36, 3e18); // FAST_ALPHA = 33e16; // 0.33
As shown above, the existing filter prices are significantly inflated by the scale of 1e18, which results in the prices being extremely skewed.
((priorValue * (1e18 - alpha)) + (currentValue * alpha)) / 1e18
((priorValue * (1e18 - 33e16)) + (currentValue * 33e16)) / 1e18
((priorValue * 67e16) + (currentValue * 33e16)) / 1e18
((2e36 * 67e16) + (3e18 * 33e16)) / 1e18
1.34e36 (1340000000000000000 ETH)
The token is supposed only to be worth around 3 ETH. However, the fast filter price wrongfully determines that it is worth around 1340000000000000000 ETH
3-07-14/src/stats/calculators/IncentivePricingStats.sol#L125
File: IncentivePricingStats.sol
125: function updatePricingInfo(IRootPriceOracle pricer, address token) internal {
..SNIP..
137: uint256 price = pricer.getPriceInEth(token);
138: 
139: // update the timestamp no matter what phase we're in
140: existing.lastSnapshot = uint40(block.timestamp);
141: 
142: if (existing._initComplete) {
143: // post-init phase, just update the filter values
144: existing.slowFilterPrice = Stats.getFilteredValue(SLOW_ALPHA, existing.slowFilterPrice, price);
145: existing.fastFilterPrice = Stats.getFilteredValue(FAST_ALPHA, existing.fastFilterPrice, price);
146: } else {
147: // still the initialization phase
148: existing._initCount += 1;
149: existing._initAcc += price;
150: 
151: // snapshot count is tracked internally and cannot be manipulated
152: // slither-disable-next-line incorrect-equality
153: if (existing._initCount == INIT_SAMPLE_COUNT) {
154: // if this sample hits the target number, then complete initialize and set the filters
155: existing._initComplete = true;
156: uint256 averagePrice = existing._initAcc * 1e18 / INIT_SAMPLE_COUNT;
157: existing.fastFilterPrice = averagePrice;
158: existing.slowFilterPrice = averagePrice;
159: }
160: }
The price returned by the stat calculators will be excessively inflated. The purpose of the stats/calculators contracts is to store, augment, and clean data relevant to the LMPs. When the solver proposes a rebalance, the strategy uses the stats contracts to calculate a composite return (score) for the proposed destinations. Using that composite return, it determines if the swap is beneficial for the vault.
If a stat calculator provides incorrect and inflated pricing, it can cause multiple implications that lead to losses to the protocol, such as false signals allowing the unprofitable rebalance to be executed.

## Recommendation
Remove the 1e18 scaling.
```solidity
if (existing._initCount == INIT_SAMPLE_COUNT) {
    // if this sample hits the target number, then complete initialize and set the filters
    existing._initComplete = true;
    uint256 averagePrice = existing._initAcc / INIT_SAMPLE_COUNT;
    existing.fastFilterPrice = averagePrice;
    existing.slowFilterPrice = averagePrice;
}
```
