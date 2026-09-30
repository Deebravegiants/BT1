# [M] User may unknowingly prevent the Keeper from executing one of his stop loss/take profit orders.

## Summary
Severity: Medium
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L377-L407
Type: audit-issue

## Details
# User may unknowingly prevent the Keeper from executing one of his stop loss/take profit orders.

## Summary
Due to the change of index  resulting from `cancel_sl_order()` or `cancel_tp_order()` execution, the user may unknowingly prevent the keeper from executing one of his stop loss/take profit orders, leading to possible losses of funds.

## Vulnerability Detail
In order to execute a Stop Loss (sl) or Take Profit (tp) order on `MarginDex`, the keeper has to call the respective function `execute_sl_order`/`execute_tp_order` passing the trade unique indentifier and the index of the respective sl/tp order. However the index of any sl/tp order is subject to change if the account responsible for the trade cancels any other sl/tp order. For example, suppose initialy we had the following sl_orders `[sl_order_A, sl_order_B, sl_order_C]`, if the account cancel `sl_order_A` (index = 0), after `cancel_sl_order()` execution the order at index=2 will be moved to index=0 (see code snippet below), resulting in the following array `[sl_order_C, sl_order_B]`.

```python
if len(trade.sl_orders) > 1:
    trade.sl_orders[_sl_order_index] = trade.sl_orders[len(trade.sl_orders) - 1]
```

This change of index of some orders can lead to problems, for example if the cancellation transaction is executed before the keeper's order, then the keeper will try to execute an order that is no longer at the right index, leading to a revert of his call. Consider the following scenario, Alice has an opened trade with the following stop loss orders (sl_orders = `[sl_order_A, sl_order_B, sl_order_C]`). Due to market fluctuation, the exchange rate cross the necessary thresholds for `sl_order_C` to be executed. The keeper monitoring those orders sends a transaction to execute the stop loss order at index 2 (`sl_order_C`). Unknowingly of the Keeper's actions, Alice also sends a transaction to cancel her stop order at index 0 (`sl_order_A`).

Given the sequence of transactions reaching the Arbitrum sequencer, it is possible for Alice's transaction (TxAlice) to be executed before the Keeper's transaction (txKeeper). Taking into account this specific transaction order in the same block, TxAlice will be the first one to be executed, modifying her trade state to sl_orders = `[sl_order_C, sl_order_B]`. Note that there is no more order at index=2 and the `sl_order_C` is now at index=0. So TxKeeper has the outdated index and `execute_sl_order()` will revert.

Therefore by cancelling one of his stop orders, Alice unknowingly prevented the Keeper from executing another of her orders. This situation can occur with both stop loss orders and take profit orders. While it is a rare occurrence, it requires both Alice and the Keeper to send transactions at similar points in time and relies on the correct ordering of transactions to happen. However, if it does occur, it can cause significant issues, especially with stop losses during market crashes. The delay of seconds between the first failed Keeper transaction and the Keeper resending a new transaction with the correct index, may result in the stop loss being executed at a significantly lower price than initially intended. Consequently, this can lead to further losses in Alice's trade.

## Impact
The reverting of the Keeper's transaction is not a problem by itself, because the Keeper can resend the transaction with the correct index later. However, the issue lies in the timely execution of certain orders, particularly stop losses. Timely execution is crucial for these types of orders since market conditions can undergo drastic changes, rendering the order useless or resulting in execution at significantly lower prices than expected. Consequently the delay caused by Keeper's transaction revert is the real issue.

As described in the protocol docs, their main objective is to make traditional centralized exchanges (CEXs) obsolete. But in order to compete with CEX, Unstoppable DEX needs to match the reliability of CEX in executing these custom orders. The current DynArray and index-based approach, while generally effective, presents a rare but potential problem for the protocol's usage, as described above.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L377-L407

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L416-L449

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L456-L471

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L478-L493

## Tool used
Manual Review

## Recommendation
Consider using HashMap instead of DynArray to store Stop Loss/Take Profit orders.
