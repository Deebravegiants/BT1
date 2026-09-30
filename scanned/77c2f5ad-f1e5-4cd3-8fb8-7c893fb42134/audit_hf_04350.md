# [H] H-02 | YesArena Block Stuﬃng Attack

## Summary
Severity: High
Contest weight: 0.1823
Dataset id: 21509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious actor may significantly increase their odds of winning the YesArena at the end of the game time by using two addresses to ensure they control both the winner and hotPotato addresses and then submitting many transactions to stuff Blast blocks for the next 2 minutes. For example:
• Bob calls deposit with address A, A is now the hot potato
• Bob calls deposit with address B, A is now the winner & B is the hot potato
• Bob submits many gas waster transactions to stuff the next 2 minutes of Blast blocks until he is the winner
This can significantly reduce the chances that other actors have at getting a deposit call recorded before the 2 minutes is over.

## Recommendation
Be aware of this risk, consider adding more time to the game for every deposit to make it more costly to block stuff the chain to improve winning odds.
