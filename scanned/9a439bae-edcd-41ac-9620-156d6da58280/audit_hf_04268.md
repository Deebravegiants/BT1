# [H] H-02 | _mintNext Unexpectedly Wraps NFT Ids

## Summary
Severity: High
Contest weight: 0.3071
Dataset id: 21302
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _mintNext function it is possible for the minted ERC721 IDs to wrap around unexpectedly, causing several potential issues for systems inheriting the DN404 contract. Consider the following scenario: User A has a balance of 3.6 erc20s. Existing totalSupply is 42.55. We _mintNext 74.43 tokens. The _mintNext function will wrap the final minted ERC721 id with the _wrapNFTId function, this is because we are attempting to mint 75 nfts to the receiver's address, however the maxId has only increased by 74. This is because: For User A: 3.6 + 74.43 = 78.03 => +75 ERC721s for User A. For totalSupply & maxId: 42.55 + 74.43 = 116.98 => +74 ERC721s allowed by maxId. As a result, the _mintNext function can unexpectedly mint ERC721 IDs that are a part of the burn pool, and burn pool NFTs will be minted without adjusting the burn pool head. Therefore when attempting to mint regularly, these newly minted NFT ids will be duplicated in the toOwned mapping and overwritten in the oo entry, effectively stealing this NFT from the user it was originally minted to with the _mintNext function.

## Proof of Concept
https://github.com/GuardianAudits/DN404PoCs/blob/3447ab536c893c77e5199a4e6fff7ee641885e2a/test/invariants/handlers/DN404Handler.sol#L392

## Recommendation
In the _mintNext function revert if the toAddress would receive more ERC721s than the maxId increase would allow, e.g. _zeroFloorSub(t.toEnd, toIndex) > (totalSupply_ / _unit()) - preTotalSupply. This behavior is also present in the _mint and _transfer functions, however there are no assumptions broken by this edge case for these functions. Therefore no code changes are necessary in these functions. Consider documenting this edge case behavior for these functions for users.
