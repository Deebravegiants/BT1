# [M] `execute_limit_order` and `execute_dca_order` may not work with tokens that revert on zero transfers.

## Summary
Severity: Medium
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L129-L191
Type: audit-issue

## Details
# `execute_limit_order` and `execute_dca_order` may not work with tokens that revert on zero transfers.

## Summary
According to the contest information provided by the sponsors "The Spot contracts need to be able to interact with any pool/token". However, there are certain situations where attempting to execute a `execute_limit_order` or `execute_dca_order` with tokens that revert on zero amount transfers will be impossible. This can temporarily block the processing of that particular order.

## Vulnerability Detail
On both `LimitOrders`'s `execute_limit_order` and `DCA`'s `execute_dca_order` functions, the profit from the order execution is shared between the caller and the protocol, as seen in the code snippet below. 

```python
if _share_profit:
    profit: uint256 = amount_out - order.min_amount_out
    self._safe_transfer(order.token_out, msg.sender, profit/2)
```

The `profit` variable can be as small as 0, for example when `amount_out == order.min_amount_out`. When `profit <= 1`, `profit/2` will round to zero and a zero amount transfer will be done to the caller. However there are some tokens that revert on such zero transfers, like `LEND`, making it impossible to execute that limit order or dca order on those market conditions.

## Impact
Some limit/dca orders may be temporarily blocked from being executed, thereby impacting the users whose orders couldn't be fulfilled. This is particularly significant for limit orders when the market direction changes, as that specific order may become impossible to execute in the future.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L129-L191

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L163-L237

## Tool used
Manual Review

## Recommendation
Consider checking if `profit > 1` before the transfer, as shown in the example code below.

```diff
diff --git a/LimitOrders.vy b/LimitOrders.mod.vy
index d7d61f6..1a12425 100644
--- a/LimitOrders.vy
+++ b/LimitOrders.mod.vy
@@ -186,7 +186,8 @@ def execute_limit_order(_uid: bytes32, _path: DynArray[address, 3], _uni_pool_fe
     # allows searchers to execute for 50% of profits
     if _share_profit:
         profit: uint256 = amount_out - order.min_amount_out
-        self._safe_transfer(order.token_out, msg.sender, profit/2)
+        if profit > 1:
+            self._safe_transfer(order.token_out, msg.sender, profit/2)

```
