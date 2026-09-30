# [M] ```MarginCallPrimaryFacet.flagShort()``` can be frontrun

## Summary
Severity: Medium
Contest weight: 0.1807
Dataset id: 7504
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Dur to the nature of primary margin call , short must be flagged before liquidation if it is below primary CR. Once flagged, 16 hours must pass before someone else could flag again. An attacker can frontrun any flagger and get himself aditional 2 hours before liquidation (instead of being liquidated after 10 hours, it's now 12 hours).

For this attack to succeed attacker need another account different than the one he is using to place shorts positions. Once it's done attacker can then frontrun any flagger that wants to flag attacker short position. Attacker open shorts. He set up his MEV bot to monitor his shorts positions. Shorts fails under primary CR. A flagger calls MarginCallPrimaryFacet.flagShort() to flag attacker shorts for liquidation. Attacker frontrun flagger and flag his own positions using MEV account. If another person had flagged his short he would only have 10 hours before he could be liquidated. But by using his own another account to frontrun the transaction, he gets additional 2 hours. Attacker now have 12 hours before he can be liquidated by anyone.

Attacker gets additional 2 hours before he can be liquidated, during 12 hours his CR can fails close to minimum CR, and this will affect protocol overal health.

## Recommendation
I recommend implementing an offchain mechanism to allow people to apply for being flaggers. Once protocol have their addresses, protocol can track them on chain using a mapping. And restrict call to MarginCallPrimaryFacet.flagShort() to only those addresses.
