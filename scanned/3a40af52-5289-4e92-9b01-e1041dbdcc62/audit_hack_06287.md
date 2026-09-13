# [H] `amount_claimable_per_share` is never reset, leading to overpay on token holder claims

## Summary
Severity: High
Reporter: ABA
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L408
Type: audit-issue

## Details
# `amount_claimable_per_share` is never reset, leading to overpay on token holder claims

## Summary

`amount_claimable_per_share` is never reset, leading to overpay on token holder claims

## Vulnerability Detail

Variable `amount_claimable_per_share` is used, as it's name suggests, to store the claimable amount per share but this variable is never reset or decreased, it's continuously increasing.

The function [`_mark_as_claimable`](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L408) which is called from [`withdraw_underlying_to_claim`](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394) sets the [value as](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419
):

```Python
self.amount_claimable_per_share += _amount * PRECISION / self.total_shares
```

This variable is used in [`_claimable_for_token`](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430) to determine the [total amount that is claimable](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L439-L440) for a position:

```Python
    total_claimable_for_position: uint256 = position.shares_owned * self.amount_claimable_per_share / PRECISION
    return total_claimable_for_position - position.amount_claimed
```

`_claimable_for_token` is used in the `claim` function [to be sent to a token holder](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L452-L459) with no further checks besides the `amount > 0` assert.

```Python
@external
def claim(_token_id: uint256) -> uint256:

    # ... 

    amount: uint256 = self._claimable_for_token(_token_id)
    assert amount > 0, "nothing to claim"

    position: Position = self.positions[_token_id]
    position.amount_claimed += amount
    self.positions[_token_id] = position
    
    ERC20(WETH).transfer(token_owner, amount)
    
    # ... 
```

This results that each time `withdraw_underlying_to_claim` is called, regardless if the tokens/shares were claimed, the amount to claim per share increases.

## Impact

The more times `withdraw_underlying_to_claim` is called the higher the payout of token holders, reaching a point where the remaining last token holders will not be able to claim anything as all the available funds were given to the first callers.

_There is also, a particular worse scenario/abuse, mentioned in a previous issue that [withdraw_underlying_to_claim is callable by anybody](https://github.com/sherlock-audit/2023-02-fair-funding-abarbatei/issues/3). Even if that is resolved and only operators can call this function, the amount claimable per share will still continue growing and be paid out more for some token holders at the expense of others_


## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L439-L440

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L452-L459

## Tool used

Manual Review

## Recommendation

Instead of cumulating the calculated `amount_claimable_per_share`, at [line 419 in Vault.vy](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L419), reset it to the new value:

```Python
def _mark_as_claimable(_amount: uint256):
     # ...

     assert ERC20(WETH).balanceOf(self) >= _amount

-    self.amount_claimable_per_share += _amount * PRECISION / self.total_shares
+    self.amount_claimable_per_share = _amount * PRECISION / self.total_shares
```
