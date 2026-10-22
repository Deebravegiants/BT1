# [M] canHedge() does not check short exposure nor

## Summary
Severity: Medium
Contest weight: 0.4626
Dataset id: 19704
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The GMXFuturesPoolHedger contract provides a utility function, canHedge(), used by
the LiquidityPool to determine if option issuance should be performed. The
function misses checks that should block option issuance under extreme
conditions.
The function canHedge() queries the GMX Vault remaining base asset amount that
can be used for hedging on line 362 and then calculates absHedgeDiff, which is the
difference between the current hedge and the expected hedge. A check is then
performed to ensure that the Vault has sufficient market depth for hedging long on
line 368 compared to absHedgeDiff. It does not perform the check for the short
side.
The current amount from an option sale is not considered in canHedge() and the
variable amountOptions on line 337 is not used. absHedgeDiff does not consider the
option amount when it performs the market depth check with the Vault's remaining.
The LiquidityPool could sell options under extreme market conditions and when it
should block option issuance.
```solidity
function canHedge(uint /* amountOptions */, bool deltaIncreasing) external view override returns (bool) {
    if (!futuresPoolHedgerParams.vaultLiquidityCheckEnabled) {
        return true;
    }
    uint spotPrice = _getSpotPrice();
    CurrentPositions memory positions = _getPositions();
    int expectedHedge = _getCappedExpectedHedge();
    int currentHedge = _getCurrentHedgedNetDeltaWithSpot(positions, spotPrice);
    if (Math.abs(expectedHedge) <= Math.abs(currentHedge)) {
        // Delta is shrinking (potentially flipping, but still smaller than current hedge), so we skip the check
        return true;
    }
    if (deltaIncreasing && expectedHedge <= 0) {
        // expected hedge is negative, and trade increases delta of the pool
        return true;
    }
    if (!deltaIncreasing && expectedHedge >= 0) {
        return true;
    }
    // remaining is the number of us dollars that can be hedged
    uint remaining = ConvertDecimals.convertTo18(
        (vault.poolAmounts(address(baseAsset)) - vault.reservedAmounts(address(baseAsset))),
        baseAsset.decimals()
    );
    uint absHedgeDiff = (Math.abs(expectedHedge) - Math.abs(currentHedge));
    if (remaining < absHedgeDiff.multiplyDecimal(futuresPoolHedgerParams.marketDepthBuffer)) {
        return false;
    }
    return true;
}
```
oolHedger.sol#L337-L372

## Recommendation
Perform an additional check for the short side and fetch the remaining quote from
GMX's Vault and compare it with absHedgeDiff.
Consider the current option amount when performing the market depth check with
GMX's Vault remaining.
