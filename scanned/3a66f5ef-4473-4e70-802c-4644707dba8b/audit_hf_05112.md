# [M] LTV of 98% would be extremely dangerous as it doesn't take into account oracle deviation

## Summary
Severity: Medium
Contest weight: 0.4580
Dataset id: 23148
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Having an LTV of 98% that pools can set is really dangerous as it doesn't take into account that oracle prices have the so-called deviation, which can be anywhere from 0.25% to 2%. Meaning that the actual LTV would be LTV + oracle1deviation + oracle2deviation, which can result in >100% LTV.
The README gives us a range for the possible LTV.
Min LTV = 10% = 100000000000000000 Max LTV = 98% =
However this range reaches up to 98% which is extremely dangerous, no matter the asset, even if the supply-borrowing pair is stablecoins.
Example oracles: stETH : ETH - 0.5% deviation DAI : ETH - 1% deviation USDC : ETH - 1% deviation USDT : ETH - 1% deviation
Both assets may be denominated in ETH, but their value is compared one to one, meaning that a user can deposit USDC to his position and borrow USDT from a pool, where both prices would be compared in terms of ETH. They will not take effect from the price of ETH, but will be affected by the extra oracle deviation, as ETH is generally around 1% - 2% and stablecoins to USD are around 0.1% (DAI : USD, USDC : USD, and so on...).
However with the above example we can see such a pool having actual LTV of 100%, as USDC can be 0.99 and USDT 1.01 with the oracle reporting both prices as 1.00 USD. In this case the pool will have 100% LTV allowing borrowers to borrow 100% of the pool causing a DOS and potentially adding some bad debt to the system. This would also discourage liquidators as they won't have any profit from liquidating these positions (once the price normalizes) and may even be at a loss.
Example of similar scenario is the recent depeg on ezETH causing Morpho to socialize some bad debt, even with reasonable LTV parameters - link.
LTV of 100% or even above would result in lenders losing their funds, as borrowers would not be incentivized to pay off their loans or would prefer to get liquidated if the price moves to their favor. Liquidators will not liquidate as they would be in a loss.

```solidity
RiskEngine.sol#L190
function acceptLtvUpdate(uint256 poolId, address asset) external {
    if (msg.sender != pool.ownerOf(poolId)) revert RiskEngine_OnlyPoolOwner(poolId, msg.sender);
    LtvUpdate memory ltvUpdate = ltvUpdateFor[poolId][asset];
    // revert if there is no pending update
    if (ltvUpdate.validAfter == 0) revert RiskEngine_NoLtvUpdate(poolId, asset);
    // revert if called before timelock delay has passed
    if (ltvUpdate.validAfter > block.timestamp) revert RiskEngine_LtvUpdateTimelocked(poolId, asset);
    // revert if timelock deadline has passed
    if (block.timestamp > ltvUpdate.validAfter + TIMELOCK_DEADLINE) {
        revert RiskEngine_LtvUpdateExpired(poolId, asset);
    }
    // apply changes
    ltvFor[poolId][asset] = ltvUpdate.ltv;
    delete ltvUpdateFor[poolId][asset];
    emit LtvUpdateAccepted(poolId, asset, ltvUpdate.ltv);
}
```

## Recommendation
Have a lower max LTV.
