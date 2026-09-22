# [M] Vault: Margin token amount is confused in open_position, add_margin and remove_margin

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503-L546
Type: audit-issue

## Details
# Vault: Margin token amount is confused in open_position, add_margin and remove_margin

## Summary

In open_position, the margin token is the debt token then swapped into position token. The margin amount no longer have a real mapping to the underlying margin token.

In add_margin and remove_margin, margin token is also debt token, but they are never swapped to/from position token. This margin amount has 1 to 1 mapping to the underlying margin token.

This leads to confusions and mistakes in other locations.

## Vulnerability Detail

For example, `margin_amount` in `_effective_leverage` assumes the underlying margin token are all debt token but parts of the margin token are postion tokens that comes from `open_position`.

```python
    margin_value: uint256 = self._in_usd(position.debt_token, position.margin_amount)
```

`margin_amount` in `remove_margin` assumes that the underlying margin tokens are all debt token but that's also not true.

## Impact

Confusions and wrong calculations in the protocol.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503-L546

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L181-L184

## Tool used

Manual Review

## Recommendation

Never swap margin in open_position. Collateral/margin should be position token in open_position originally.
