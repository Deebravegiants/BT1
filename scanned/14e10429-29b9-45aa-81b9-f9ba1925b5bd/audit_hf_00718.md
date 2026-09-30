# [M] M-11 | Value Extraction Via Trustless Keepers

## Summary
Severity: Medium
Contest weight: 0.1556
Dataset id: 2269
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Orders may be executed by any actor as soon as they are ready which allows for several potential value extraction or grieﬁng mechanisms. For example:
1. An attacker creates two accounts
2. The attacker watches the mempool and when they see that a trader will be positively impacted for an order that is going to be committed, the attacker creates two orders with these two accounts in order to sandwich trader. All 3 orders are committed in the same block.
3. When all 3 orders are ready, the attacker can sandwich the trader with their two orders and settle all 3 of these orders by calling the settleOrder function.
4. The attacker gets positively impacted by their two orders via negatively impacting user who was expecting positive impact
Although the limit price of the order will limit how much can be stolen, users are not likely to set their priceLimit ahead of the market price to lock in any positive impact.

## Recommendation
The ultimate prevention for malicious keepers would be to use either a centralized, or semi-centralized but punishable keeper system. However, if the current keeper setup is maintained, users should be informed that they must set the price limit such that they can capture any positive price impact that they expect to receive. But this also comes with a caveat such that their order may not get ﬁlled if the skew changes naturally in the next 12 seconds before their order becomes executable.
