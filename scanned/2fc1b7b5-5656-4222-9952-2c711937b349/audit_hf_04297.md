# [C] C-01 | Risk Free Trades With cancellationReceiver

## Summary
Severity: Critical
Contest weight: 0.2958
Dataset id: 21436
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PoC In the cancelOrder function if the order is an increase or swap order, which requires input funds, these funds are sent back to the cancellationReceiver. When the cancellationReceiver address is the OrderVault the transferOut function will revert with the SelfTransferNotSupported error. As a result a malicious actor may create a MarketIncrease order with the following properties:
• The cancellationReceiver is the OrderVault
• The swapPath includes a market that would fail it’s reserves validation as a result of the swap The order fails as the initial swap for the increase order cannot go through, but the order cannot be cancelled as the cancellationReceiver is the OrderVault. Therefore the order will remain in the OrderStore until the malicious actor sees that price has moved in their favor relative to the range of prices that their MarketIncrease order may be executed with. The malicious actor can then deposit into the market in the swapPath which was previously failing the reserve validation, such that it no longer fails the reserve validation and the order can be executed. The malicious actor then realizes a risk-free proﬁt. If price should not move in the actor’s favor during the 5 minute max price age period after their order’s requestExpiration time, then the actor may update their order and attempt the risk free trade over the next period.

## Recommendation
Upon order creation validate that the cancellationReceiver is not the address of the OrderVault.
