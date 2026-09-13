# [M] `Vault::reduce-position` results in a loss of funds

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L288-L336
Type: audit-issue

## Details
# `Vault::reduce-position` results in a loss of funds

## Summary

The `Vault` contract has a `reduce_position` function that can be used to partially close an existing position by selling some of the underlying token. Both the debt and margin are reduced proportionally to preserve the leverage ratio.

However, the reduced margin is never credited back to the trader. This means that they can never withdraw the full amount of margin they deposited. The amount it was reduced by is lost.

## Vulnerability Detail

The logic in `reduce_position` that handles the sell and reduction of margin is as follows...

```vyper
		amount_out_received: uint256 = self._swap(
        position.position_token, position.debt_token, _reduce_by_amount, min_amount_out
    )

    # reduce margin and debt, keep leverage as before
    reduce_margin_by_amount: uint256 = (
        amount_out_received * margin_debt_ratio / PRECISION
    )
    reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount

    position.margin_amount -= reduce_margin_by_amount
```

You can see that the `position.margin_amount` is reduced, but this amount is never allocated back the to trader. The `reduce_margin_by_amount` should be added to the traders margin stored in `self.margin[position.account][position.debt_token]`

## Impact

When reducing a position, the trader loses funds that were used as margin.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L288-L336

## Tool used

Manual Review

## Recommendation
Add the `reduce_margin_by_amount` to the traders margin so it can be withdrawn.

```diff
    position.margin_amount -= reduce_margin_by_amount
+   self.margin[position.account][position.debt_token] += reduce_margin_by_amount
```
