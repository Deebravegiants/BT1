# [H] Vault: position could not be liquidated if account margin is less than penalty

## Summary
Severity: High
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L372
Type: audit-issue

## Details
# Vault: position could not be liquidated if account margin is less than penalty

## Summary

The liquidation penalty is deducted from user's account margin. If user's account margin is less than penalty, his postion could not be liquidated.

## Vulnerability Detail

`self.margin[position.account][position.debt_token] -= penalty` will revert if account margin is less than penalty.

```solidity
    # penalize account
    penalty: uint256 = debt_amount * self.liquidation_penalty / PERCENTAGE_BASE

    if amount_out_received > debt_amount:
        # margin left
        remaining_margin: uint256 = amount_out_received - debt_amount
        penalty = min(penalty, remaining_margin)
        self.margin[position.account][position.debt_token] -= penalty
```

## Impact

User can empty his account margin to make his position unliquidatable.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L372

## Tool used

Manual Review

## Recommendation

Deduct penalty from position margin.
