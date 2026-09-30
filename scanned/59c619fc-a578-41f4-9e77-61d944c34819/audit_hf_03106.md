# [M] CallOption NFT holder may lose funds on a custodial marketplace.

## Summary
Severity: Medium
Contest weight: 0.1176
Dataset id: 17514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the CallOption NFT holder lists the NFT on a custodial marketplace then they may lose the spread sent on settlement. If the CallOption NFT holder sends it to a custodial marketplace for listing where it's not sold until settlement then the spread amount will be transferred to the address of the custodial marketplace which may not be claimable by the CallOption NFT holder. CallOption NFT holder loses access to the spread amount they are entitled to on expiry and settlement of option.

## Recommendation
Consider changing from the push model to a pull model for transferring the spread and strike price amounts ie. allowing the owner of the CallOption NFT to redeem the spread and then burn the nft. Added mapping to track eth amounts to be claimed by option owner and claimOptionProceeds external function to access the claimable eth https://github.com/hookart/protocol/pull/53 Ok. Claimable by owner if settled by someone else. claimOptionProceeds() has a reentrancy. Add nonReentrant modifier and also follow CEI pattern by caching optionClaims[optionId] in a local variable and deleting it before making the _safeTransferETHWithFallback call. Thanks Rajeev, this is resolved here: https://github.com/hookart/protocol/pull/72?no-redirect=1 Verified fix.
