# [M] Slippage could be 0 in some places allowing the user to suffer sandwich attacks

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L307-L311
Type: audit-issue

## Details
# Slippage could be 0 in some places allowing the user to suffer sandwich attacks

## Summary
In some functions from the contracts `SwapRouter` & `Vault`, we can find some calls to the Uniswap V3 functions where their `amountOutMinimum` is not validated, so it could be potentially 0; allowing external bots to sandwich attack the swap transaction and make the user lose lots of funds.

## Vulnerability Detail
In some places of the protocol, they are checking the received `amountOutMinimum` value to not be 0, to protect the user from potential sandwich attacks (for example, [here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L307-L311)). But not in every part of the code is implemented that check so it can cause severe loses to the users.

## Impact
If for some reason (like not checked in the front-end, or a thrid-party creates a front-end, or even if a user wants to interact directly with the contract) an invalid `min_amount_out` parameter is sent in some of the core functions; the contract won't validate it and it will perform the swap without any slippage protection. It will affect to functions like the one to open the position, so it is a fairly frequent issue.

## Code Snippet
Places where the issue is happening:
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L77-L98
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L101-L120
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L181-L184
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L728
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L157

## Tool used
Manual Review

## Recommendation
Implement a similar validation to the one the protocol already implemented in other parts of the code, like in the `_close_position` from the `Vault` contract [here](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L244-L249):
```vyper
    min_amount_out: uint256 = _min_amount_out
    if min_amount_out == 0:
        # market order, add some slippage protection
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, position.position_amount
        )
```
