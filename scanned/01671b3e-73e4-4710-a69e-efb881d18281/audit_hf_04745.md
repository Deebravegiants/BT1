# [M] Borrow fees can be arbitrarily increased with-

## Summary
Severity: Medium
Contest weight: 0.5959
Dataset id: 22579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SpotHedgeBaseMaker LPs can maximize their LP returns by closing their trades against other whitelisted makers. The whitelisted makers, which the SpotHedgeBaseMaker and the OracleMaker are, can receive borrowing fee based on their utilization ratio and don’t need to pay borrowing fee themselves. The borrowing fee is meant to be compensation for providing liquidity to the market, but makers like the SpotHedgeBaseMaker, which are able to hedge their position risk, can arbitrarily increase their utilization ratio by opening positions against the OracleMaker, and immediately closing them against the SpotHedgeBaseMaker, maximizing their fees without having to provide liquidity over time. An attacker can choose a specific market direction, then monitor the utilization of the OracleMaker. Any time the OracleMaker's utilization is flat, the attacker would open a position in the chosen market direction against the OracleMaker (to minimize the dynamic premium), then immediately close the position by offsetting it with a taker order against the SpotHedgeBaseMaker. The only risk the attacker has to take is holding the position for the approximately ~2 second optimism block time, until they're able to offset the position using the ClearingHouse to interact directly with the SpotHedgeBaseMaker. Value extraction in the form of excessive fees, at the expense of traders on the other side of the chosen position direction. Utilization does not take into account whether the taker is reducing their position, only that the maker is increasing theirs:
```solidity
// File: src/borrowingFee/LibBorrowingFee.sol : LibBorrowingFee.updateReceiverUtilRatio()
#1
/// spec: global_ratio = sum(local_ratio * local_open_notional) / total_receiver_open_notional
/// define factor = local_ratio * local_open_notional;
global_ratio = sum(factor) / total_receiver_open_notional
/// we only know 1 local diff at a time, thus splitting factor to known_factor and other_factors
/// a. old_global_ratio = (old_factor + sum(other_factors)) / old_total_open_notional
/// b. new_global_ratio = (new_factor + sum(other_factors)) / new_total_open_notional
/// every numbers are known except new_global_ratio. sum(other_factors) remains the same between old and new
/// expansion formula a: sum(other_factors) = old_global_ratio * old_total_open_notional - old_factor
/// replace sum(other_factors) in formula b:
/// new_global_ratio = (new_factor + old_global_ratio * old_total_open_notional - old_factor) / new_total_open_notional
uint256 oldUtilRatioFactor = self.utilRatioFactorMap[receiver];
50 @> uint256 newTotalReceiverOpenNotional = self.totalReceiverOpenNotional;
uint256 oldUtilRatio = self.utilRatio;
uint256 newUtilRatio = 0;
if (newTotalReceiverOpenNotional > 0) {
    // round up the result to prevent from subtraction underflow in next calculation
    55 @> oldUtilRatio * self.lastTotalReceiverOpenNotional + newUtilRatioFactor - oldUtilRatioFactor,
    newTotalReceiverOpenNotional
);
59:
}
/src/borrowingFee/LibBorrowingFee.sol#L40-L59
```
and whitelisted makers never have to pay any fee:
```solidity
// File: src/borrowingFee/BorrowingFee.sol : BorrowingFee.getPendingFee()
#2
function getPendingFee(uint256 marketId, address trader) external view override returns (int256) {
166 @> if (_isReceiver(marketId, trader)) {
        return _getPendingReceiverFee(marketId, trader);
    }
    return _getPendingPayerFee(marketId, trader);
170:
}
/src/borrowingFee/BorrowingFee.sol#L165-L170
```

## Recommendation
There is no incentive to reduce utilization, and I don't see a good solution that doesn't involve the makers having to actively re-balance their positions, e.g. force makers to also have to pay the fee, and only pay the fee to the side that has the largest net non-maker open opposite position
