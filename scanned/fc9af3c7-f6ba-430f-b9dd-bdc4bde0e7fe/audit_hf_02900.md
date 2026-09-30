# [H] SQDF-2 | Weak Source of Randomness

## Summary
Severity: High
Contest weight: 0.1103
Dataset id: 16201
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
pickWinner uses weak sources of on-chain randomness. A validator can exploit this in order to
obtain a winner that is beneﬁcial to themselves.
In addition, an Admin can keep calling pickWinner, then reportResult to clear isCompetitionEnded,
then call pickWinner again and so on until the winner is favorable to them.

## Recommendation
Utilize a strong source of randomness whether it be the on-chain randomness pattern or an oracle. In
addition, prevent repeated calls to pickWinner by tracking whether a winner was already chosen.
