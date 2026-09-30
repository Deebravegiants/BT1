# [H] H-01 | _mintNext Allows NFTs In The Burn Pool To Be Stolen

## Summary
Severity: High
Contest weight: 0.1790
Dataset id: 21301
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _mintNext function ignores the burn pool tokenIds, and mints directly starting from the existing totalSupply / unit() + 1 id. However this id and the ids that follow can be within the burn pool. As a result burn pool NFTs will be minted without adjusting the burn pool head. Therefore when attempting to mint regularly, these newly minted NFT ids will be duplicated in the toOwned mapping and overwritten in the oo entry, effectively stealing this NFT from the user it was originally minted to with the _mintNext function.

## Proof of Concept
https://github.com/GuardianAudits/DN404PoCs/blob/main/test/guardian/PoCs.t.sol#L40

## Recommendation
Do not allow the burn pool feature to be used in tandem with the _mintNext function, otherwise refactor the _mintNext function to account for the burn pool.
