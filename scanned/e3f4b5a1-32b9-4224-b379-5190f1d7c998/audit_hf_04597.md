# [M] M-31 | Asp Rewards Can Be Sandwiched

## Summary
Severity: Medium
Contest weight: 0.0768
Dataset id: 22202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The idea of AutoCompoundingPodLp is to swap the accumulated rewards into paired lp tokens and use them to generate new spTokens. When the current reward token of the asp doesn't match the reward token for its pod, 0 slippage is used for the swap so anyone can sandwich the transaction to benefit from it which will result in a loss for the asp holders. The following can be executed in one transaction:
• swap
• process rewards
• swap again

## Recommendation
Consider adding an adequate slippage parameter to the swaps and a try/catch as well to not introduce a new way of DOS-ing the asp.
