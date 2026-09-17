# [H] A position is liquidateable immediately upon opening position close to max leverage

## Summary
Severity: High
Reporter: 0xDjango
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157-L209
Type: audit-issue

## Details
# A position is liquidateable immediately upon opening position close to max leverage

## Summary
A position can be opened and immediately liquidated due to faulty checks for its final effective leverage.

## Vulnerability Detail
When opening a position, an early `assert` statement ensures that the positions debt to margin ratio is less than or equal to the max leverage for the debt token.

`assert ((_debt_amount + _margin_amount) * PRECISION / _margin_amount) <= self.max_leverage[_debt_token][_position_token] * PRECISION, "too much leverage"`

The issue: **Since the final `position_amount` is the result of a DEX swap, it will ALWAYS be lower than the debt+margin amount, resulting in an effective leverage larger than the max leverage**

There is no check at the end of the `open_position()` function to ensure that the received swap amount does not result in a liquidateable position.

## Impact
- Near max-leverage position openings can be immediately liquidated

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157-L209

## Tool used
Manual Review

## Recommendation
Add a check at the end of `open_position()` to check that the position is not liquidateable.
