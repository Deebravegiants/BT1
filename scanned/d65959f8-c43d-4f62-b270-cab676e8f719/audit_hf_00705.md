# [M] M-04 | Leverage Mismatch Because Different Price Sources

## Summary
Severity: Medium
Contest weight: 0.1369
Dataset id: 2256
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the LeveragedToken’s redeemFor method, the redemption amount is reduced by a “decaying redemption fee” plus a slippage deduction (intended to represent expected order fees and price impact). Ordinarily, these fees stay in the contract or go to other token holders. However, if the user redeeming is the last, meaning he redeems the entire totalSupply, there are no other holders to beneﬁt from these leftover fees and the contract itself can no longer distribute them. That portion of sUSD remains stuck in the PerpsV2 protocol as unused margin. The ﬁnal user is penalized, losing this fraction of their redeemable amount for no net beneﬁt to the system. On the other hand, this also happens if the LeveragedToken currently has no position as it dropped below 100 sUSD and the rebalancer closed it. In that case it is not fair to remove this slippage amount from the user and distributing it among the other users.

## Recommendation
When leveragedTokenAmount = totalSupply, skip collecting the decaying redemption fee and slippage.
