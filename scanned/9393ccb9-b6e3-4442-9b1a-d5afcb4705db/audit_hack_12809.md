# [H] Leverage calculation is wrong

## Summary
Severity: High
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L465-L477
Type: audit-issue

## Details
# Leverage calculation is wrong

## Summary
Leverage calculation is wrong which will lead to unfair liquidations or over leveraged positions depending on price movements.

## Vulnerability Detail
`_calculate_leverage` miscalculate the leverage by using `_debt_value + _margin_value` as numerator instead of `_position_value `:

[Vault.vy#L465-L477](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L465-L477)
```solidity
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

The three inputs of the function `_position_value`, `_debt_value` and `_margin_value` are all determined by a chainlink oracle price feed.
`_debt_value` represents the value of the position's debt share converted to debt amount in USD.
`_margin_value` represents the current value of the position's initial margin amount in USD.
`_position_value` represents the current value of the position's initial position amount in USD.

The problem with the above calculation is that `_debt_value + _margin_value` does not represent the value of the position. The leverage is the ratio between the current value of the position and the current margin value. `_position_value - _debt_value` is correct and is the current margin value, but `_debt_value + _margin_value` doesn't represent the current value of the position since there is no guarantee that the debt token and the position token have correlated price movements.

Example: debt token: ETH, position token: BTC.
- Alice uses 1 ETH of margin to borrow 14 ETH (2k USD/ETH) and get 1 BTC (30k USD/BTC) of position token. Leverage is 14.
- The next day, the price of ETH in USD is still 2k USD/ETH but BTC price in USD went down from 30k to 29k USD/BTC. Leverage is now (`_position_value == 29k`) / (`_position_value == 29k` - `_debt_value == 28k`) = 29, instead of what is calculated in the contract: (`_debt_value == 28k + _margin_value == 2k`) / (`_position_value == 29k` - `_debt_value == 28k`) = 30.


## Impact
Leverage calculation is wrong which will lead to unfair liquidations or over leveraged positions depending on price movements.

## Code Snippet
[Vault.vy#L465-L477](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L465-L477)

## Tool used

Manual Review

## Recommendation
Consider modifying the code like this:

```solidity
def _calculate_leverage(
    _position_value: uint256, _debt_value: uint256, _margin_value: uint256
) -> uint256:
    if _position_value <= _debt_value:
        # bad debt
        return max_value(uint256)


    return (
        PRECISION
-       * (_debt_value + _margin_value)
+       * (_position_value)
        / (_position_value - _debt_value)
        / PRECISION
    )
```
