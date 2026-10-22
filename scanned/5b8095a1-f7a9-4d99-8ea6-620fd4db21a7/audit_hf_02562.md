# [M] Missing Deadline Checks Allow Pending Transactions To Be MaliciouslyExecutedForconvert(),buyPortalEnergy()andsellPortalEnergy() Functions

## Summary
Severity: Medium
Contest weight: 0.1688
Dataset id: 13733
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Portal.sol contract does not allow users to submit a deadline for convert() action. This missing feature enables pending transactions to be maliciously executed at a later point. The following scenario can happen:

1. Alice wants to convert 1,000,000 PSM tokens for 100 X tokens. She signs the transaction calling Portal.convert() with _token = X token address and _minReceived = 99 X tokens to allow for some slippage.

2. The transaction is submitted to the Mempool, however, Alice chose a transaction fee that is too low for miners to be interested in including her transaction in a block. The transaction stays pending in the Mempool for extended periods, which could be hours, days, weeks, or even longer.

3. When the average gas fee drops far enough for Alice’s transaction to become interesting again for miners to include it, her conversion will be executed. In the meantime, the price of X token could have drastically changed. She will still at least get 99 X tokens due to _minReceived, but the X token value of that output might be significantly lower. She has unknowingly performed a bad conversion due to the pending transaction she forgot about.

## Recommendation
Introduce a deadline parameter to the mentioned functions.
function X(
    uint256 deadline
) external nonReentrant {
    if (deadline < block.timestamp) revert DeadlineExpired();
    ...
}
