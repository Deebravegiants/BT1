# [M] Some Token's like `USDT` do not have a return value on `transfer`.

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67C1-L67C64
Type: audit-issue

## Details
# Some Token's like `USDT` do not have a return value on `transfer`.

## Summary
Some tokens do not implement the `ERC20` standard properly but are still accepted by most code that accepts `ERC20` tokens. For example, `Tether` (`USDT`)'s transfer() and transferFrom() functions on L1 do not return booleans as the specification requires and instead have `no return value`.
**Note** ----> This report is different from my previous report that had to do with `unchecked return value` ___Here I'm tackling the fact that some `ERC20 tokens` that are widely used do not have return values, and they are not tackled properly in the protocol.
## Vulnerability Detail
This is an instance.
```vyper
       ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
```
## Impact
where the return values are not known failed transfer's will fail silently.
## Code Snippet
> **These lines are all the instances of the bug in the protocol.**

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67C1-L67C64
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161C1-L161C83
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L184C1-L184C78
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L189C2-L189C67
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L251C1-L251C52
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L220C1-L220C47
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L189C1-L189C129
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L171C1-L171C77
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L334C1-L334C47
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L201C2-L201C97
## Tool used

Manual Review

## Recommendation
Use OpenZeppelin’s SafeERC20's safeTransfer()/safeTransferFrom() instead
