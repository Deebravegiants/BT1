# [M] If an auction has no bidder,the NFT ownership

## Summary
Severity: Medium
Contest weight: 0.1173
Dataset id: 17714
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The lenders in principal have the claim for the loan collateral, but current rule will let the liquidation caller get the collateral for free. Effectively take advantage from the vault LP, which is not fair. After the endAuction(), the collateral will be released to the initiator. Essentially, the initiator gets the NFT for free. But the lenders of the loan take the loss. However, the lenders should have the claim to the collateral, since originally the funds are provided by the lenders. If the collateral at the end is owned by whoever calls the liquidation function, it is not fair for the lenders. And will discourage future users to use the protocol.  
• Lenders could suffer fund loss in some cases.  
• The unfair mechanism will discourage future users.

## Recommendation
If there is no bidder for the auction, allow the NFT to get auctioned for another chance.
