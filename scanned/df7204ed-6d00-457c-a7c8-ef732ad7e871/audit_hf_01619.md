# [M] Missing input sanitization

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 8725
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are a few instances within the project where lack of checks can lead to problems.
The payoutDelta function takes two input parameters - startDay and untilDay to return payout and shares:
```solidity
function payoutDelta(uint256 startDay, uint256 untilDay) external view
returns(uint256 payout, uint256 shares) { //@audit - require that untilDay > startDay
    TotalStore memory start = totals[startDay];
    TotalStore memory until = totals[untilDay];
    unchecked {
        return (
            until.payout - start.payout,
            until.shares - start.shares
        );
    }
```
However, there is no check that the untilDay > startDay and an underflow can occur inside the unchecked box if start.payout and start.shares are greater than until.payout and until.shares.
The same is true for the payoutDeltaTrucated function where the function will revert if untilDay > startDay.
```solidity
function payoutDeltaTrucated(
    uint256 startDay,
    uint256 untilDay,
    uint256 multiplier
) external view returns(uint256 payout) {
    return (
        (
            (totals[untilDay].payout - totals[startDay].payout) * multiplier *
            (untilDay - startDay)
        ) / (totals[untilDay].shares - totals[startDay].shares)
        // for a 1 day span, the amount is actually known
        (untilDay - startDay) - 1
    );
}
```
Another instance where a check is required is the collectUnattributedPercent function:
```solidity
* @param basisPoints the number of basis points (100% = 10_000)
function collectUnattributedPercent(
    uint256 basisPoints
) external returns(uint256 amount) {
    uint256 unattributed = _getUnattributed(token);
    amount = (unattributed * basisPoints) / TEN_K; //@audit if unattributed * basisPoints) < 10k it will round down to zero
    _collectUnattributed(token, transferOut, recipient, amount, unattributed);
}
```
As we can see from the comment, the input parameter basisPoints should not be greater than (100% = 10_000). However, any value can be passed including number greater than 10_000.

## Recommendation
Add appropriate checks to avoid any unexpected results and reverts.
