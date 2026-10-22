# [M] M-01 | NFT Marketplaces Will Not Read Royalty Info

## Summary
Severity: Medium
Contest weight: 0.0889
Dataset id: 22376
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Token contract implements the ERC2981 standard to signal royalty fees to be taken when NFT sales are made on NFT marketplaces. However the Token contract is the ERC20 compatible contract, not the ERC721 compatible contract, therefore NFT exchanges which will interact with the DN404Mirror contract will not read the royaltyRecipient and royaltyFee that are conﬁgured in the Token contract. As the team currently does not planning on utilizing the royalty feature, the severity of the omission is limited.

## Recommendation
Create a contract which inherits DN404Mirror and implements the ERC2981 standard with the royalty conﬁgurations. Consider adding a function to update the bps for future-proofing.
