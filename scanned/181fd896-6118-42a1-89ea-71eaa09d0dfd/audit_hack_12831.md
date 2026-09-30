# [M] Vault: reduced margin is not added back to account

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L320-L330
Type: audit-issue

## Details
# Vault: reduced margin is not added back to account

## Summary

In reduce_position, the reduced margin is deducted from position but is not added back to account.

## Vulnerability Detail

```python
    # reduce margin and debt, keep leverage as before
    reduce_margin_by_amount: uint256 = (
        amount_out_received * margin_debt_ratio / PRECISION
    )
    reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount

    position.margin_amount -= reduce_margin_by_amount                       # <----- margin is reduced from postion

    burnt_debt_shares: uint256 = self._repay(position.debt_token, reduce_debt_by_amount)
    position.debt_shares -= burnt_debt_shares
    position.position_amount -= _reduce_by_amount
```

## Impact

The user loses margin when they partially close their position.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L320-L330

## Tool used

Manual Review

## Recommendation

Add reduced margin back to account.

```diff
  position.margin_amount -= reduce_margin_by_amount
+ self.margin[position.account][position.debt_token] += reduce_margin_by_amount
```
