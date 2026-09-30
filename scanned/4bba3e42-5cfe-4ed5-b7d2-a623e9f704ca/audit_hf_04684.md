# [M] Attacker can make first time taker's loose their

## Summary
Severity: Medium
Contest weight: 0.4041
Dataset id: 22448
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Attacker can make first time taker's loose their funds by inflating fees
For first time taker buy orders, there is a matchOrderFee which is calculated in the _matchSpotOrder function as shown below:
if (o.takerSide) {
takerFee = BasicMath.mul(o.baseQuantity, product.takerFee);
makerFee = BasicMath.mul(quoteQuantity, product.makerFee);
if (o.isFirstTime) {
=>
takerFee += BasicMath.div(
txFees[MATCH_ORDER_TX_FEE_INDEX],
o.executionPrice
);
}
}
Since BasicMath.div does division in e18, ie. mutliplies by e18 before the division, an attacker can make the taker pay a large amount of fees by keeping a really low execution price. This will hugely inflate the fees of the taker. To minimize the loss of the attacker for selling at a low price, the attacker can keep a low quantity
A likely scenario is the beginning, when there are no opposite-side orders currently on the orderbook
First time takers loose funds
```

## Recommendation
Enforce price limit checks / collect the fees always in core collateral / use oracle price for conversion
