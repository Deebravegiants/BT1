# [M] Upgradable escrow contract

## Summary
Severity: Medium
Contest weight: 0.0856
Dataset id: 1597
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upgradable escrow contract poses great risk to user who approved their NFT to the contract. Most popular token / NFT exchange do not require user to approve their asset to admin upgradable contract.

This also increases user gas usage because they would have to revoke approval when they are done with the protocol.

## Recommendation
Separate the escrow contract to make it non-upgradable with a restricted set of functionality.
This is an interesting suggestion. I’m not sure if the recommendation really reduces the risk though. If we were to make the escrow portion immutable, the trust still depends on the upgradeable market contract to do the correct thing. If I’m understanding the suggestion correctly, the terms of the deal would still be defined in the upgradeable contract - so even with an immutable escrow manager we could theoretically upgrade the market to allow us to `buy` each of the NFTs for 0 ETH.
