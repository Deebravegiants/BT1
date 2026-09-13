# [M] There is no minimum amount required when using the `Vault.open_position`. The fee can be bypassed.

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157
Type: audit-issue

## Details
# There is no minimum amount required when using the `Vault.open_position`. The fee can be bypassed.

## Summary

The fee in `Vault.open_position` is based on the `token_in_amount`. If `token_in_amount ` is too small, there is no fee that will be charged.

## Vulnerability Detail


 There is no minimum amount required when using the `Vault.open_position`. `token_in_amount * self.trade_open_fee / PERCENTAGE_BASE` could be zero.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L202
```vyper
def open_position(
    _account: address,
    _position_token: address,
    _min_position_amount_out: uint256,
    _debt_token: address,
    _debt_amount: uint256,
    _margin_amount: uint256,
) -> (bytes32, uint256):
    …

    token_in_amount: uint256 = _debt_amount + _margin_amount
    …

    # charge fee
    fee: uint256 = token_in_amount * self.trade_open_fee / PERCENTAGE_BASE
    …
```

A user can intentionally split a large position to many small positions and bypass the fee.

## Impact

The fee can be bypassed in `Vault.open_position`

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L202

## Tool used

Manual Review

## Recommendation

Implement a lower bound for `token_in_amount` in `Vault.open_position`
