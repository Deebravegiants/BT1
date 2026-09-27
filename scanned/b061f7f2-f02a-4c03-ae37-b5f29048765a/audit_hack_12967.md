# [M] `execute_dca_order` can get frontrunned, causing bots to lose gas fees and disincentivizing them to act.

## Summary
Severity: Medium
Reporter: n1punp
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L194-L198
Type: audit-issue

## Details
# `execute_dca_order` can get frontrunned, causing bots to lose gas fees and disincentivizing them to act.

## Summary
`execute_dca_order` can get frontrunned, causing bots to lose gas fees and disincentivizing them to act.

## Vulnerability Detail
- The `execute_dca_order` relies on bots to execute the DcaOrder by swapping tokens from the user. However, the execution can be reverted if the token approval is insufficient, which can occur in case the user frontruns the transaction by approving 0 to the contract, leaving the transaction reverted.

## Impact
- Execute tx will revert, causing the execution bot to lose gas fees for free. (the gas fee used will be larger than what the attacker needs, since the attacker only needs to approve 0).

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L194-L198

## Tool used

Manual Review

## Recommendation
- Lock the user's tokens for DCA order in some contracts instead
