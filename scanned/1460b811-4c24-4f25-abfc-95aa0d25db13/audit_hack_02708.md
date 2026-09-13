# [M] Exploiter can deposit to Queue reaching maxTVL to block other from depositing without any risk

## Summary
Severity: Medium
Reporter: minhquanym
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L86
Type: audit-issue

## Details
# Exploiter can deposit to Queue reaching maxTVL to block other from depositing without any risk

## Summary
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/QueueInternal.sol#L86

## Vulnerability Detail
User needs to deposit to Queue first before their funds can be deposit to Vault. However there is a `maxTVL` limit in Queue, limiting how much funds all users can deposit in total.

In addition to that, as long as the epoch is not start, user can withdraw their funds from the Queue. So a whale/exploiter can deposit to reach maxTVL at the beginning of the epoch, effectively block other from depositing, and withdraw right before this epoch end.

## Impact
Normal users cannot deposit to Queue

## Code Snippet

The check for `maxTVL` in `_deposit()` function
```solidity
// the maximum total value locked is the sum of collateral assets held in
// the queue and the vault. if a deposit exceeds the max TVL, the transaction
// should revert.
uint256 totalWithDepositedAmount =
    Vault.totalAssets() + ERC20.balanceOf(address(this));
require(totalWithDepositedAmount <= l.maxTVL, "maxTVL exceeded");
```

## Tool used

Manual Review

## Recommendation

Consider adding some penalty for withdrawing from Queue before epoch start
