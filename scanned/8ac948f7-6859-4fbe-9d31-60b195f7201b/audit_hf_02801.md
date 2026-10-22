# [H] MJR-1 "Sandwich attack" on user withdrawal

## Summary
Severity: High
Contest weight: 0.0185
Dataset id: 15239
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a classic sandwich attack that can be triggered during a user‑initiated withdrawal when the strategy contract performs an automated market maker (AMM) token swap inside the same transaction. The root cause is that the swap is executed without any slippage protection or price verification, allowing an attacker who observes the pending withdrawal to place a trade that moves the market price just before the user’s swap (front‑run) and then reverse the trade immediately after (back‑run). By doing so the attacker inflates the price the user receives, causing the user’s withdrawal to be settled at an unfavorable rate. This can result in the user receiving less of the expected token, or in extreme cases the protocol losing value because the swap extracts value from the pool. The attack can only be carried out when the withdrawal path includes a direct AMM swap and when the attacker can monitor the mempool and act within the same block, conditions that are relatively rare but not impossible. All users who request a withdrawal are affected, as they may see their balance reduced unexpectedly, and the protocol’s overall liquidity can be eroded over time. The issue was discovered during a manual security audit that examined the flow of funds in the withdrawal function and identified the lack of slippage checks. It is hard to notice because the failure manifests only under specific market conditions and the user interface typically shows a successful transaction without indicating that the received amount is lower than expected. To remediate the problem the swap operation should be protected with a maximum slippage parameter, use a trusted price oracle, or be moved out of the user‑controlled transaction so that the price cannot be manipulated by a front‑runner. In essence, the bug belongs to the class of price‑manipulation vulnerabilities caused by unchecked AMM interactions within privileged functions, leading to a mismatch between expected and actual refund amounts and breaking the accounting assumptions of the protocol.

## Recommendation
Although vulnerability conditions are rare and hard to exploit, it is recommended to protect AMM DEX swap operations with slippage technique.
