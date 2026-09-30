# [H] UB-2 | Order of Operations

## Summary
Severity: High
Contest weight: 0.1043
Dataset id: 16212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The logic does not correctly calculate the gain due to the SafeMath order of operations. With the SafeMath operations the addition is performed first, but what is needed is to first calculate the winner’s part of the loser funds and then finally adding it to BettorBetWinner. For example: 3.add(10).mul(3).div(6) = 6 3 + 10 * 3 / 6 = 8

## Recommendation
Replace with BettorBetWinner + bets[result.loser] * BettorBetWinner / bets[result.winner].
