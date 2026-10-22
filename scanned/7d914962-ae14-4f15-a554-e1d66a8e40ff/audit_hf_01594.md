# [H] _rebalanceWithdraw() mechanism in glAVAX allows arbitrage opportunities by changing the shares/AVAX ratio

## Summary
Severity: High
Contest weight: 0.1841
Dataset id: 8566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The balance available for withdrawals is tracked in address(this).balance. The implementation itself is correct and users will have enough liquidity to withdraw given enough balance is accumulated. However, withdrawing should be done atomically; AVAX should not be withdrawn when withdraws are rebalanced and the shares burned when the requests are fulfilled. Essentially, whenever possible changing the ratio shares/wAVAX ratio should be avoided to prevent MEV opportunities.

## Proof of Concept
no pocwas pushed. In short, instead of withdrawing AVAX and keeping it in the glAVAX contract, a reserved wAVAX amount is tracked, always keeping the shares/wAVAX ratio intact.

## Recommendation
Recommendation not found
