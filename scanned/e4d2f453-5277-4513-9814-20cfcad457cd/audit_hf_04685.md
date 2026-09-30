# [H] OrderDispatch._matchOrder incorrectly reduces

## Summary
Severity: High
Contest weight: 0.6382
Dataset id: 22449
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
OrderDispatch._matchOrder function is used to match one taker order with 1 or more maker orders. To reuse order signatures, Crucible stores the filled quantity of each order, so the real "active" order quantity = order quantity - order filled quantity.
The problem is that taker order quantity is reduced by filled quantity inside the maker orders loop, meaning that taker order quantity is reduced multiple times instead of just once:
for (uint j; j < makerLength; j++) {
...
order.taker.quantity -= crucible.filledQuantitys(order.takerDigest);
order.maker.quantity -= crucible.filledQuantitys(order.makerDigest);
...
// handle filled quantitys
crucible.updateFilledQuantity(
order.takerDigest,
order.makerDigest,
uint128(baseQuantity)
);
// emit event to show order matched
emit Events.OrderMatched();
}
This means that accounting will be completely wrong if taker order is matched with more than 1 maker order (which is very likely for large taker orders).
OrderDispatch._matchOrder function is called from force swap and from match order actions sent by off-chain app. The problem described above happens when at least 3 maker orders are matched with 1 taker order.
Here is an example of what happens with 3 maker orders:
1. Taker = 8 (filled = 0), maker1 = 1, maker2 = 2, maker3 = 5
2. Matching with maker1: taker = 8 - 0. baseQuantity = min(8,1) = 1. filled (taker) = 1
3. Matching with maker2: taker = 8 - 1 = 7. baseQuantity = min(7,2) = 2. filled (taker) = 3
4. Matching with maker3: taker = 7 - 3 = 4. baseQuantity = min(4,5) = 4. filled (taker) = 7
In the end - taker order is filled for a quantity = 7 instead of 8, maker3 is also not fully filled. In such scenario the result is just unexpected (taker order will remain in the orderbook instead of filling completely). However, the following actions which don't expect these user position sizes might do something unexpected. For example, if the following action in the same transaction is withdrawal, and the user is left with a larger position (closing smaller than expected), since health check is only off-chain, and off-chain app didn't expect such user position, on-chain withdrawal will be allowed, even if the user becomes unhealthy/liquidatable after it.
Also, the same code in many scenarios will simply revert. For example:
1. Taker = 11 (filled = 0), maker1 = 5, maker2 = 5, maker3 = 1
2. Matching with maker1: taker = 11 - 0. baseQuantity = min(11,5) = 5. filled (taker) = 5
3. Matching with maker2: taker = 11 - 5 = 6. baseQuantity = min(6,5) = 5. filled (taker) = 10
4. Matching with maker3: taker = 6 - 10 => reverts
This is much more common and much more severe issue, which will basically cause all transactions from off-chain app to ingresso to revert, both matching and all the others together with them, meaning the protocol will fail to function completely.
Any time a taker order is matched with 3+ makers, either the accounting is broken or the matching transaction reverts (and will keep reverting when off-chain app tries to execute it again and again).
If the accounting is broken, the taker and the last maker(s) will have unexpected positions and moreover, since withdrawal on-chain logic doesn't check account health, if order match and withdrawals are combined in the same transaction, due to unexpected positions, the withdrawal will succeed, but the users might remain with larger than expected position causing them to be immediately liquidated or cause bad debt.
```

## Recommendation
Move reduction of order.taker.quantity by filled quantities to before the makers loop, reduce order.taker.quantity by baseQuantity at the same time with increasing filled quantities.
