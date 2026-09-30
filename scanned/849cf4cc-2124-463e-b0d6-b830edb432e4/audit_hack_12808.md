# [H] Adding margin mistakenly increases leverage and removing margin decreases leverage

## Summary
Severity: High
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L527-L546
Type: audit-issue

## Details
# Adding margin mistakenly increases leverage and removing margin decreases leverage

## Summary
Adding and removing margin have the opposite effect on the position's effective leverage due to an error in the `_effective_leverage()` calculation.

Removing margin actually makes the position more healthy. The reason for this is that the position's `position_amount` is not reduced when removing margin, and vice versa.

## Vulnerability Detail
`remove_margin()` simply reduces the positions `margin_amount` which is in the numerator of the leverage calculation:

```solidity
    return (
        PRECISION
        * (_debt_value + _margin_value)
        / (_position_value - _debt_value)
        / PRECISION
    )
```

Per the function's doc string: 

```solidity
def remove_margin(_position_uid: bytes32, _amount: uint256):
    """
    @notice
        Allows to remove margin from a Position and 
        increase the leverage.
    """
```

The leverage should be increased, but it is in fact decreased.

***Example:***
- Debt = 400
- Margin = 100
- Position value = 500
- Current leverage = (400 + 100) / (500 - 400) = **5**

*Removing margin...*

- Debt = 400
- Margin = 0
- Position value = 500
- Current leverage = (400 + 0) / (500 - 400) = **4**

Removing margin should also decrement the `position_amount` used in the denominator of the leverage calculation.

## Impact
- Removing and adding margin have opposite effects on position health. This can be gamed to create bad debt and unliquidateable loans.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L527-L546

## Tool used
Manual Review

## Recommendation
It doesn't seem right to have `margin_amount` in the numerator of the effective leverage calculation.
