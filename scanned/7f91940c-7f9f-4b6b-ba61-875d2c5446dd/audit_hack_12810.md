# [M] Vault: position margin should be valued in postion token but not debt token

## Summary
Severity: Medium
Reporter: n33k
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L458
Type: audit-issue

## Details
# Vault: position margin should be valued in postion token but not debt token

## Summary

In `_effective_leverage`, margin value is valued in debt token. But the margin is already swapped into position token at open_postion. So it should be valued in position token.

## Vulnerability Detail

This is how margin value is calculated in _effective_leverage,

```python
    position_value: uint256 = self._in_usd(
        position.position_token, position.position_amount
    )
    debt_value: uint256 = self._in_usd(position.debt_token, debt_amount)
    margin_value: uint256 = self._in_usd(position.debt_token, position.margin_amount)

    return self._calculate_leverage(position_value, debt_value, margin_value)
```

I will give an example to demonstrate that this calculation is incorrect.

For 1x leverage postion, debt amount is zero, and `_calculate_leverage` should always return 1.

```python
def _calculate_leverage(
    _position_value: uint256, _debt_value: uint256, _margin_value: uint256
) -> uint256:
    if _position_value <= _debt_value:
        # bad debt
        return max_value(uint256)

    return (
        PRECISION
        * (_debt_value + _margin_value)
        / (_position_value - _debt_value)
        / PRECISION
    )
```

The result will become `margin value/position value`. Postion value is valued in postion token while margin value is vauled in debt token. The leverage will not always be 1.

## Impact

`_effective_leverage` will give the wrong leverage which will result in incorrect liquidation.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L458

## Tool used

Manual Review

## Recommendation

Value position margin in postion token.
