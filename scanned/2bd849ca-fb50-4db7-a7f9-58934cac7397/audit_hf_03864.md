# [M] Risk of Unfair Order Execution Price in_validateOrdersA

## Summary
Severity: Medium
Contest weight: 0.4865
Dataset id: 20131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While the system seems to have appropriate checks in place for order matching, a potential risk exists around the order execution pricing logic, specifically when the orders are placed in the same block. In such cases, the system currently selects the sell order price as the fill price. This may not be fair for the buyer, who may end up paying more than necessary.
In the _validateOrdersAndDetermineFillPrice function, when two orders are placed in the same block, the fill price is set as the price of the sell order (orders[1]). This is potentially unfair because it could lead to a scenario where the buyer is paying the maximum possible price, even when the sell order was potentially willing to sell at a lower price.
This could affect the trust of participants in the exchange, particularly those who frequently make buy orders. The unfair pricing might result in monetary losses for these participants, leading to a negative perception of the platform.
```solidity
if (blockPlaced0 < blockPlaced1) {
    mode0 = OrderExecutionMode.Maker;
    fillPrice = orders[0].price;
} else if (blockPlaced0 > blockPlaced1) {
    mode1 = OrderExecutionMode.Maker;
    fillPrice = orders[1].price;
} else { // both orders are placed in the same block, not possible to determine what came first in solidity
    // executing both orders as taker order
    mode0 = OrderExecutionMode.SameBlock;
    mode1 = OrderExecutionMode.SameBlock;
    // Bulls (Longs) are our friends. We give them a favorable price in this corner case
    fillPrice = orders[1].price;
}
```
otocol/contracts/orderbooks/OrderBook.sol#L288-L300

## Proof of Concept
To reproduce this vulnerability:
1. Deploy the smart contract on a local testnet or Ethereum mainnet fork.
2. Place two orders: a buy order and a sell order within the same block with different prices.
3. Once the orders are matched and executed, check the execution price.
4. You will notice that the execution price is exactly the same as the sell order, regardless of the buy order's price.
traders when they place their orders. Traders who are willing to trade at the execution price would not consider this a problem, while others might see it as an unfair pricing practice.

## Recommendation
A more fair approach might be to calculate the average of the buy order and sell order prices, which might better reflect the market conditions at the moment both orders were made. In case of any restrictions for using the average price, a price setting rule that better approximates a fair market price should be used.
