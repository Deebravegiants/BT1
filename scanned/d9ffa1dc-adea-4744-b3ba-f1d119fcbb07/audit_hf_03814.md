# [H] Limit swap orders can be used to get a free

## Summary
Severity: High
Contest weight: 0.6352
Dataset id: 20038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can cancel their limit swap orders to get a free look at prices in future blocks. This is a part of the same issue that was described in the last contest. The sponsor states that any swap limit order submitted in block range N can't be executed until block range N+2, because the block range is forced to be after the submitted block range, and keepers can't execute until the price has been archived, which necessarily won't be until after block range N+1. Consider what happens when half of the oracle's block ranges are off from the other half, e.g.:
1 2 3 4 5 6 7 8 9 < block number  
O1: A B B B B C C C D  
O2: A A B B B B C C C  
^^ grouped oracle block ranges  
At block 1, oracles in both groups (O1 and O2) are in the same block range A, and someone submits a large swap limit order (N). At block 6, oracles in O1 are in N+2, but oracles in O2 are still in N+1. This means that the swap limit order will execute at the median price of block 5 (since the earliest group to have archive prices at block 6 for N+1 will be O1) and market swap order submitted at block 6 in the other direction will execute at the median price of block 6 since O2 will be the first group to archive a price range that will include block 6. By the end of block 5, the price for O1 is known, and the price that O2 will get at block 6 can be predicted with high probability (e.g. if the price has just gapped a few cents), so a trader will know whether the two orders will create a profit or not. If a profit is expected, they'll submit the market order at block 6. If a loss is expected, they'll cancel the swap limit order from block 1, and only have to cover gas fees. Essentially the logic is that limit swap orders will use earlier prices, and market orders use current prices; an attacker is able to know both prices before having their orders executed, and use large order sizes to capitalize on small price differences. There is a lot of work involved in calculating statistics about block ranges for oracles and their processing time/queues, and ensuring one gets the prices essentially when the keepers do, but this is likely less work than co-located high frequency traders in traditional finance have to do, and if there's a risk free profit to be made, they'll put in the work to do it every single time, at the expense of all other traders. Market orders can use the current block, but limit orders must use the next block:
```solidity
// File: gmx-synthetics/contracts/order/SwapOrderUtils.sol : SwapOrderUtils.validateOracleBlockNumbers()
if (orderType == Order.OrderType.MarketSwap) {
    OracleUtils.validateBlockNumberWithinRange(
        minOracleBlockNumbers,
        maxOracleBlockNumbers,
        orderUpdatedAtBlock
    );
    return;
}
if (orderType == Order.OrderType.LimitSwap) {
    if (!minOracleBlockNumbers.areGreaterThan(orderUpdatedAtBlock)) {
        revert Errors.OracleBlockNumbersAreSmallerThanRequired(minOracleBlockNumbers, orderUpdatedAtBlock);
    }
    return;
}
revert Errors.UnsupportedOrderType();
```
gmx-synthetics/contracts/order/SwapOrderUtils.sol#L57-L74

## Recommendation
All orders should follow the same block range rules
