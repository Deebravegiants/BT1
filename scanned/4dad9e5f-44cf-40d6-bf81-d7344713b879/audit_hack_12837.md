# [M] Allowance was not set to zero first before changing the allowance

## Summary
Severity: Medium
Reporter: chainNue
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204
Type: audit-issue

## Details
# Allowance was not set to zero first before changing the allowance

## Summary

Allowance was not set to zero first before changing the allowance

## Vulnerability Detail

As mentioned in README,

> The Margin DEX has whitelisted tokens/markets anyways, so lets assume WETH, wBTC, ARB, USDC, USDT + default OZ ERC20 implementations as scope.

The USDT is in scope.

Certain ERC20 tokens, such as USDT, have limitations when it comes to modifying the allowance from a non-zero value. For instance, the approve() function of Tether (USDT) will throw an error if the current approval is not set to zero. This safeguard is in place to prevent unauthorized alterations of approvals and mitigate the risk of front-running attacks.

In several files, the approve function being called with input is the amount requested, and no initial approve to zero

```python
File: Dca.vy
203:     # approve UNISWAP_ROUTER to spend amount token_in
204:     ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in_per_execution)

File: LimitOrders.vy
163:     # approve UNISWAP_ROUTER to spend amount token_in
164:     ERC20(order.token_in).approve(UNISWAP_ROUTER, order.amount_in)

File: SwapRouter.vy
68:     ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
```

## Impact

Failed to approve the token, will resulting in failed transfer of the token, which is not expected by the protocol.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L204

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L164

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L68

## Tool used

Manual Review

## Recommendation

It is recommended to set the allowance to zero before increasing the allowance.
