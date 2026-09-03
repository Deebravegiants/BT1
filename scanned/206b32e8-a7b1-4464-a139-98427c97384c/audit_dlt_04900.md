# [M] If a erc721 is  a weird erc721/erc1155  where there is 2 nfts with the same token id  the other one can be sent to address 0

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/64
Type: sherlock-finding

## Details
simon135

medium

# If a erc721 is  a weird erc721/erc1155  where there is 2 nfts with the same token id  the other one can be sent to address 0

## Summary
If there is an erc1155 or a weird erc721 that has 2 nfts with the same tokenId then there can be a situation that one is funded but the other is  in the contract and it can be sent to address(0) and cause loss of funds 
## Vulnerability Detail
steps:
ex: nft name is noodle
nft =   noodle  and tokenId=1
and its sent to the contract 
and there is another one sent to the contract
The first one works as promised and is sent to the  `recipient`
but the other one  an attacker can call `withdrawToken()` with an the same order  since 
the recipient is address(0) the nft will be lost.
Plus the checks and effects are not followed here in case the erc721 has `ontransfer` functionality.

 
## Impact
the second nft will be lost 
It's a medium because it either has to be weird erc721 or erc1155 and the protocol has to approve it but with out knowing about the nft this can be an issue of loss of funds.
## Code Snippet
```solidity 
    function withdrawToken(bytes32 orderHash, uint256 tokenId) public {
        address collection = matchedOrders[uint256(orderHash)].collection;

        address recipient = withdrawableCollectionTokenId[collection][tokenId];

        // Transfer NFT to recipient
        IERC721(collection).safeTransferFrom(address(this), recipient, tokenId);

        // This token is not withdrawable anymore
        withdrawableCollectionTokenId[collection][tokenId] = address(0);

        emit WithdrawnToken(orderHash, tokenId, recipient);
    }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/64_
