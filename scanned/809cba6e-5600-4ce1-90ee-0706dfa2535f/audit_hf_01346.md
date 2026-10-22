# [M] M-4 Unsafe safeApprove and safeIncreaseAllowance.

## Summary
Severity: Medium
Contest weight: 0.0935
Dataset id: 6755
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• CurveHandler.sol#L246
• CurveHandler.sol#L266
Version 4.8.0 of safeApprove and safeIncreaseAllowance (SafeERC20.sol#L46-L68) is currently in use.
USDT approve method (it checks that allowance is zero):
function approve(
address _spender,
uint _value
) public onlyPayloadSize(2 * 32) {
...
require(!((value != 0) && (allowed[msg.sender][spender] != 0)));
allowed[msg.sender][spender] = value;
...
}
In the current implementation, if the ConicPool is left with an extra allowance for CurvePool, then users will not be able to withdraw their tokens due to revert.

## Recommendation
We recommend doing approve(0) before calling the main approve (currently OpenZeppelin contracts have this logic SafeERC20.sol#L52).
