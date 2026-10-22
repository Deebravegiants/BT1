# [M] M-10 LpToken taint grieﬁng

## Summary
Severity: Medium
Contest weight: 0.1808
Dataset id: 6741
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LpToken.sol cannot be minted or burned by a user if someone has transferred an amount of LpToken to them greater than controller.getMinimumTaintedTransferAmount(token):
function _ensureSingleEvent(address ubo, uint256 amount) internal {
if(
!controller.isAllowedMultipleDepositsWithdraws(ubo) &&
amount > controller.getMinimumTaintedTransferAmount(address(this))
) {
require(
_lastEvent[ubo] != block.number,
"cannot mint/burn twice in a block");
...
LpToken.sol#L81
This means a malicious actor could send a minimum number of tokens to any "whale" (a user with a large balance) trying to make a large deposit or withdraw, thereby blocking their operation.
For example, this could be used to attack users who want to urgently burn their LP tokens to repay an overcollateralized debt and avoid liquidation. This can also be used to block MEV bots that utilize mint or burn lp tokens in their path strategies. It also removes the ability to buy LP tokens on an exchange and burn them in a single transaction.
It's worth noting that by default, controller.getMinimumTaintedTransferAmount(token) equals zero, so the attacker would only need to pay for the gas to block a specific user's operations.

## Recommendation
We recommended allowing users to burn LP tokens received before the current taint.
For instance, if in the first block a user mints 1000 tokens for themselves, and then in the second block they receive another token, it would be desirable in the second block to still allow them to burn the initial 1000 tokens. However, it should revert if they try to burn more than that amount.
