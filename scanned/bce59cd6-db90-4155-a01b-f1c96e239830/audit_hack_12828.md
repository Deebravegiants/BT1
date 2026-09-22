# [H] The reduced margin doesn't return to the trader in `Vault.reduce_position`.

## Summary
Severity: High
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L326
Type: audit-issue

## Details
# The reduced margin doesn't return to the trader in `Vault.reduce_position`.

## Summary

When executing `Vault.reduce_position`, the position tokens are sold. The debt and the margin  are reduced. However, the reduced margin doesn’t return to the trader, leading to a loss of funds.

## Vulnerability Detail

`Vault.reduce_position` decreases position.margin_amount, but it doesn’t return the reduced margin to the trader.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L326
```vyper
def reduce_position(
    _position_uid: bytes32, _reduce_by_amount: uint256, _min_amount_out: uint256
) -> uint256:
    …

    position.margin_amount -= reduce_margin_by_amount

    …
```
This reduced margin should go back to the trader.
```vyper
self.margin[position.account][position.debt_token] += reduce_margin_by_amount
```


## Impact

The reduced margin doesn’t return to the trader, leading to a loss of funds.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L326

## Tool used

Manual Review

## Recommendation

```diff
def reduce_position(
    _position_uid: bytes32, _reduce_by_amount: uint256, _min_amount_out: uint256
) -> uint256:
    …

    position.margin_amount -= reduce_margin_by_amount
+   self.margin[position.account][position.debt_token] += reduce_margin_by_amount

    …
```
