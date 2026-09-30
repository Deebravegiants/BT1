# [M] On tax sells, swaps are vulnerable to MEV

## Summary
Severity: Medium
Contest weight: 0.0262
Dataset id: 16153
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of allowing a token swap operation to proceed with a minimumAmountOut parameter set to zero. This design choice, common for tax‑bearing tokens that deduct a fee on transfer, removes any slippage protection from the transaction. Because the contract does not enforce a lower bound on the amount of output tokens that must be received, a malicious actor can observe the pending transaction in the mempool and submit a competing transaction that changes the price or consumes the liquidity before the victim's swap is executed. The attacker can therefore force the victim’s swap to execute at an unfavorable rate, often resulting in the victim receiving far fewer tokens than expected or even zero tokens, while the attacker captures the value difference. The issue manifests whenever a user initiates a sell or swap of a tax token through a function that hard‑codes minimumAmountOut to 0, typically in decentralized exchanges or router contracts that support taxed assets. It affects any user who relies on the swap to receive a predictable amount of tokens, as well as the broader protocol that may suffer from reduced trust and potential loss of liquidity. The problem was identified during a manual audit that highlighted the absence of slippage checks for taxed token swaps. It can be difficult to notice because a zero minimum amount out is sometimes justified as a workaround for tax‑related rounding errors, and the contract may still appear to function correctly under normal market conditions. To remediate the issue, the contract should calculate an appropriate minimumAmountOut based on current market rates, incorporate a configurable slippage tolerance, or use a price oracle to enforce that the output amount cannot fall below a reasonable threshold, thereby preventing front‑running exploitation and preserving user expectations of receiving a non‑zero amount of tokens.

## Recommendation
Recommendation not found
