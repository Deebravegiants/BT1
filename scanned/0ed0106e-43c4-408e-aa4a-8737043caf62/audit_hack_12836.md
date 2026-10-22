# [M] Unsafe approve would make some core functions to always revert

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L68
Type: audit-issue

## Details
# Unsafe approve would make some core functions to always revert

## Summary
In the `SwapRouter`, `Dca`, `LimitOrders` & `Vault` contracts there are some `approve` calls that do not handle non-standard ERC20 behaviors. That will make those core functions to always revert.

## Vulnerability Detail
The protocol states that the Margin Dex should support tokens like USDT; but some tokens like that one have a non-standard ERC20 behavior when calling the `approve` function (https://github.com/d-xo/weird-erc20#approval-race-protections).

Some tokens (e.g. USDT, KNC) do not allow approving an amount `M > 0` when an existing amount `N > 0` is already approved, reverting the transaction.

## Impact
Since one of the tokens affected is `USDT`, which is a very common trading token, this issue is highly likely to happen.

## Code Snippet
- `SwapRouter`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L68
- `Vault`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L395
- `Dca`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204
- `LimitOrders`: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L164

## Tool used
Manual Review

## Recommendation
To handle this behavior, change the code to "approve" first a 0 amount:
```vyper
+ ERC20(_token_in).approve(UNISWAP_ROUTER, 0)
ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
```
