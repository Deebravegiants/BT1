# [H] Missing checkpoint on APY change will create unfair interest and rewards

## Summary
Severity: High
Contest weight: 0.7749
Dataset id: 6067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _pendingTPS(StorageStaking storage $) private view returns (uint256) {
    if ($.totalDeposited == 0) return $.tps;
    /* solhint-disable-next-line not-rely-on-time */
    uint256 secondsPassed = block.timestamp - $.lastCheckpoint;
    // We need double rounding here to avoid situations where borrowers repay less
    // than what is due to lenders. With division in formulas, a surplus is unavoidable,
    // but it must favor the pool and not the lender, because in the latter case
    // we simply cannot pay off.
    uint256 r1 = ($.apy * secondsPassed * $.utilization) / (APY_DENOMINATOR * 365 days);
    uint256 r2 = (r1 * TPS_DENOMINATOR) / $.totalDeposited;
    return $.tps + r2;
}

function _pendingInterest(
    StorageStaking storage $,
    address borrower
) private view returns (uint256) {
    Debt storage debt = $.debts[borrower];
    /* solhint-disable-next-line not-rely-on-time */
    uint256 secondsPassed = block.timestamp - debt.timestamp;
    return (debt.borrowed * secondsPassed * $.apy) / (APY_DENOMINATOR * 365 days);
}
```
The problem arises when the APY is changed:
```solidity
function _setApy(uint32 apy) internal {
    _setApy(_storageStaking(), apy);
}
// ...
function _setApy(StorageStaking storage $, uint32 apy) private {
    $.apy = apy;
}
```
No checkpoint is made before applying the new APY, it affects all interest retroactively from the last checkpoint. This results in unfair interest accumulation: • For lenders: Their rewards calculation via TPS will be retroactively changed. • For borrowers: The interest on their loans will be calculated using the new rate for the entire loan period.

## Recommendation
Call the _checkpoint function before setting the new APY. For individual borrowers, maintain a history of APY changes along with their timestamps and calculate accrued interest for each change interval accordingly.
