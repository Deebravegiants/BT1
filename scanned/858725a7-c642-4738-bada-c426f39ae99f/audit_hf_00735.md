# [H] H-05 | Locked Dispute Bonds After Escalation Reset

## Summary
Severity: High
Contest weight: 0.1782
Dataset id: 2291
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a dispute is resolved by the council and its escalation leads to a Reset result, any user with an
“unclosed dispute” bond remains unable to claim it because reopenMarketForDisputes sets
marketClosedForDisputes to false.
Consequently, once the market transitions to a new proposal, if it finalizes with no disputes, the
dispute is never recognized as “closed” or “canceled,” preventing claimUnclosedDisputeBonds from
succeeding. The disputer’s bond remains locked, and they are unable to recover their funds.

## Recommendation
Update canDisputorClaimbackBondFromUnclosedDispute to allow bond retrieval if the market has
been reset, rather than strictly requiring it to be “closed for disputes” or “finalized.” This ensures no
user is stuck with an unclaimable dispute bond after the escalation reset.
