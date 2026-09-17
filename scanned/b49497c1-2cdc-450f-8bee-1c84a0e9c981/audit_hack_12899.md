# [M] Vault: If all postion amount is reduced in reduce_position, the position margin is forever locked

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L252-L257
Type: audit-issue

## Details
# Vault: If all postion amount is reduced in reduce_position, the position margin is forever locked

## Summary

It is position to reduce all position amount via `reduce_position`. The result zero amount position could not be closed by `close_position`. Margin inside the position is forever locked.

## Vulnerability Detail

In `reduce_position`. It is possible to reduce all position amount.

```python
assert position.position_amount >= _reduce_by_amount, "_reduce_by_amount > position"
```

Then a zero amount position is left which can not be closed by close_position. Because close_position will make a zero amount input swap which will revert inside uniswap.

```python
    amount_out_received: uint256 = self._swap(
        position.position_token,
        position.debt_token,
        position.position_amount,
        min_amount_out,
    )
```

## Impact

User's position margin is forever locked.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L252-L257

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L304

## Tool used

Manual Review

## Recommendation

Make sure `_reduce_by_amount` is not equal to `position_amount`.

```python
assert position.position_amount > _reduce_by_amount, "_reduce_by_amount > position"
```
