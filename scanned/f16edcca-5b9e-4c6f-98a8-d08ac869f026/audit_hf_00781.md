# [M] The current implementation is incompatible with `WBTC` as collateral token

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 2426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The original Liquity V2 code is designed to work with collateral tokens that have 18 decimal places (WETH, rETH, wstETH). BitVault, however, intends to use WBTC and other BTC-like tokens as collateral, which only have 8 decimal places.

This difference in decimal precision introduces many issues, as many core calculations - such as collateral ratios, interest accruals, redemptions, and liquidations - are written with the assumption of 18-digit precision. The problem is systemic and scattered across many parts of the codebase. While not all instances are immediately exploitable, the cumulative effect will lead to incorrect behaviour, wrong calculations, broken incentives, and many other issues.

Due to the scope of this issue, I highlight a few cases in this report. However, the full impact requires a detailed audit of the whole system to ensure it correctly accounts for 8 decimal collateral assets.

**Example 1: Incorrect gas compensation cap for liquidations** During liquidation, the total funds the liquidator receives are: `WETH gas compensation + min(0.5% of Trove’s collateral, 2 units of collateral token)` The following function determines the collateral portion of the compensation:

```solidity
// Return the amount of Coll to be drawn from a trove collateral and sent as gas compensation.
function _getCollGasCompensation(uint256 _entireColl) internal pure returns (uint256) {
    return LiquityMath._min(_entireColl / COLL_GAS_COMPENSATION_DIVISOR, COLL_GAS_COMPENSATION_CAP);
}
```

With constants defined as:

```solidity
// Fraction of collateral awarded to liquidator
uint256 constant COLL_GAS_COMPENSATION_DIVISOR = 200; // dividing by 200 yields 0.5%
uint256 constant COLL_GAS_COMPENSATION_CAP = 2 ether; // Max coll gas compensation capped at 2 ETH
```

As we can observe, the cap here is in 2e18, meaning the liquidator can exceed the cap of 2 units of collateral token.

**Example 2:** In `TroveManager` we have the following function, in which I highlight the decimal precision of the parameters:

```solidity
function _getCollPenaltyAndSurplus(
    uint256 _collToLiquidate, // 8 decimals
    uint256 _debtToLiquidate, // 18 decimals
    uint256 _penaltyRatio, // most likely 8 decimals
    uint256 _price // unclear, assume 18 or 8 decimals
) internal pure returns (uint256 seizedColl, uint256 collSurplus) {
    uint256 maxSeizedColl = (_debtToLiquidate * (DECIMAL_PRECISION + _penaltyRatio)) / _price;
    if (_collToLiquidate > maxSeizedColl) {
        seizedColl = maxSeizedColl;
        collSurplus = _collToLiquidate - maxSeizedColl;
    } else {
        seizedColl = _collToLiquidate;
        collSurplus = 0;
    }
}
```

Since `_collToLiquidate` is in 8 decimals (WBTC), and `maxSeizedColl` is computed using 18-decimal debt and price values, the comparison is unreliable. The if condition can never be true.

**Example 3: Redistribution rewards calculation fails due to decimal mismatch** In `_getLatestTroveData`, redistribution gains are calculated as:

```solidity
trove.redistBoldDebtGain = (stake * (L_boldDebt - rewardSnapshots[_troveId].boldDebt)) / DECIMAL_PRECISION;
trove.redistCollGain = (stake * (L_coll - rewardSnapshots[_troveId].coll)) / DECIMAL_PRECISION;
```

However:

* `stake` is in 8 decimals (WBTC),
* `L_boldDebt` and `L_coll` are updated respectively with 18 decimal and 8 decimal values (see `TroveManager::_redistributeDebtAndColl()`)
* `DECIMAL_PRECISION` is 1e18

Result:  
`trove.redistBoldDebtGain` results in values with 8 decimal precision, which may still work but significantly reduces the granularity. `trove.redistCollGain` becomes effectively zero, since the numerator ends up far smaller than the 1e18 divisor (e.g., 1e8 * 1e8 / 1e18 = 0.01).

These are just a few examples where the precision mismatch leads to broken calculations. Fully enumerating all such cases would make the report overly lengthy, but these are sufficient to demonstrate the associated risks.

Additionally, many other calculations rely heavily on consistent decimal precision across components like oracle prices and collateral ratios. Without further clarification from the team on how these values are standardized across the system, it’s difficult to assess the full scope of potential issues.

## Recommendation
No recommendation
