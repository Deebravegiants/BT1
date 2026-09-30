# [M] Griefing risk in mint

## Summary
Severity: Medium
Contest weight: 0.2575
Dataset id: 17984
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[CidNFT.sol#L147-L157](https://github.com/code-423n4/2023-01-canto-identity/blob/dff8e74c54471f5f3b84c217848234d474477d82/src/CidNFT.sol#L147-L157)  
[CidNFT.sol#L177-L182](https://github.com/code-423n4/2023-01-canto-identity/blob/dff8e74c54471f5f3b84c217848234d474477d82/src/CidNFT.sol#L177-L182)

`CidNFT.mint()` has an optional parameter `_addList` that enables users to register subprotocol NFTs to the CID NFT right after the mint.

However, there is no guarantee that the `_cidNFTID` encoded in `_addList` is the same ID as the newly minted NFT. If there is a pending mint transaction and another user frontrun the mint transaction with higher fee, the previous transaction will revert as the `_cidNFTID` is no longer the expected ID.

[CidNFT.sol#L177-L182](https://github.com/code-423n4/2023-01-canto-identity/blob/dff8e74c54471f5f3b84c217848234d474477d82/src/CidNFT.sol#L177-L182)
    
    address cidNFTOwner = ownerOf[_cidNFTID];
    if (
        cidNFTOwner != msg.sender &&
        getApproved[_cidNFTID] != msg.sender &&
        !isApprovedForAll[cidNFTOwner][msg.sender]
    ) revert NotAuthorizedForCIDNFT(msg.sender, _cidNFTID, cidNFTOwner);

A malicious actor can grief this by frontrunning users that try to mint with non-zero `_addList`, causing their mint transaction to fail.

In absence of malicious actor, it is also possible for this issue to happen randomly during busy period where a lot of users are trying to mint at the same time.

## Proof of Concept
* The next CidNFT mint ID is `1000`.
  * Alice wants to mint and prepares `_addList` with the expected `_cidNFTID` of `1000`.
  * Bob saw Alice’s transaction and frontran her, incrementing the next minting ID to `1001`.
  * Alice’s transaction tries to add subprotocol NFTs to ID `1000` which is owned by Bob. This causes the transaction to revert.

## Recommendation
Modify mint so that the minted ID is the one used during the add loop, ensuring that mint will always succeed.

Although this submission and [H-01](https://github.com/code-423n4/2023-01-canto-identity-findings/issues/67) both share a common root cause of frontrunning mints and colliding CidNFT ids in the `CidNFT.add` function, it is essential to note that the impact of each issue is significantly different and therefore warrant to be kept separate.
