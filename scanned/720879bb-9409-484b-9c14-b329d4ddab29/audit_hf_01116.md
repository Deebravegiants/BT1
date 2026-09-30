# [H] Price could have a max drop even if it has oversold

## Summary
Severity: High
Reporter: deadrosesxyz
Contest weight: 0.8631
Dataset id: 4587
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol utilizes a dutch-auction bonding curve. The idea is that the price drops until the point where volume picks up. To put it very simply, if not enough tokens are bought, price drops more. And ideally, if enough tokens are bought, token's price starts rising.
```solidity
// Get the expected amount sold and the net sold in the last epoch
uint256 expectedAmountSold = _getExpectedAmountSoldWithEpochOffset(0);
int256 netSold = int256(totalTokensSold_) - int256(state.totalTokensSoldLastEpoch);
state.totalTokensSoldLastEpoch = totalTokensSold_;
// Possible if no tokens purchased or tokens are sold back into the pool
if (netSold <= 0) {
    adjustmentTick = upperSlugPosition.tickLower;
    accumulatorDelta += _getMaxTickDeltaPerEpoch();
} else if (totalTokensSold_ <= expectedAmountSold) {
    // Safe from overflow since we use 256 bits with a maximum value of (2**24-1) * 1e18
    adjustmentTick = currentTick;
    accumulatorDelta += _getMaxTickDeltaPerEpoch()
        * int256(WAD - FullMath.mulDiv(totalTokensSold_, WAD, expectedAmountSold)) / I_WAD;
} else {
```
The problem is however in the current implementation. The first check on which depends the price movement is the epoch-to-epoch movement. As we can see, if netSold <= 0, nothing else is considered and price has a max drop. This is even in the cases where tokens are sold in excess to many upcoming epochs. For example, til end of epoch 2, there might be sold the quota that should usually be until epoch 4. Then, if in epoch 3, the netSold is <= 0, there will be a significant drop in price, even though there are more tokens sold than what is usually expected for said epoch.
This could be extremely problematic in scenarios where a token has rapidly picked up momentum which temporarily stagnates throughout an epoch. Such price could easily make the whole token crash as new users would be able to buy it at significantly lower price.

Impact Explanation:
Issue could potentially crash the whole economics surrounding a token, therefore should be High severity.

## Proof of Concept
Attaching 2 tests. In both of them assets have been sold in excess for next epochs. In one of the tests just 1 wei is bought in the following epoch, while in the other no more assets are bought. Because of this, price drops ~800 ticks:
```solidity
function test_offByOne1() public {
    vm.warp(hook.getStartingTime() + hook.getEpochLength());
    uint256 expectedAmountSold = hook.getExpectedAmountSoldWithEpochOffset(3); // this should return
    PoolKey memory poolKey = key;
    buy(int256(expectedAmountSold));
    vm.warp(hook.getStartingTime() + 2 * hook.getEpochLength());
    buy(1);
    sell(1);
    vm.warp(hook.getStartingTime() + 3 * hook.getEpochLength());
    bool isToken0 = hook.getIsToken0();
    int24 tick = hook.getCurrentTick(poolKey.toId());
    console.log(isToken0);
    console.log(tick);
    buy(1);
    tick = hook.getCurrentTick(poolKey.toId());
    console.log(tick);
}

function test_offByOne2() public {
    vm.warp(hook.getStartingTime() + hook.getEpochLength());
    uint256 expectedAmountSold = hook.getExpectedAmountSoldWithEpochOffset(3); // this should return
    PoolKey memory poolKey = key;
    buy(int256(expectedAmountSold));
    vm.warp(hook.getStartingTime() + 2 * hook.getEpochLength());
    buy(1);
    // sell(1);
    vm.warp(hook.getStartingTime() + 3 * hook.getEpochLength());
    bool isToken0 = hook.getIsToken0();
    int24 tick = hook.getCurrentTick(poolKey.toId());
    console.log(isToken0);
    console.log(tick);
    buy(1);
    tick = hook.getCurrentTick(poolKey.toId());
    console.log(tick);
}
```

## Recommendation
First check should be whether expected assets are met and only if they're not, check if netBought is non-positive.
