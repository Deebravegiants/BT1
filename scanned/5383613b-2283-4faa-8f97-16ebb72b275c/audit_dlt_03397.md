# [M] function receiveNFTs does not check if amount > 0

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-nftx
Published: 2021-05-10
Source: https://github.com/code-423n4/2021-05-nftx-findings/issues/27
Type: code-finding

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
When is1155 is true, function receiveNFTs iterates over all the tokens and updates holdings and quantity1155. If the quantity1155 is 0 for that token, it adds this token to the holdings set. However, it does not check that the amount is greater than 0, thus it is possible to push the same token to the hodlings multiple times as quantity1155 still remains 0.

## Recommended Mitigation Steps
Solution: check that amount > 0 if is1155 is true. Also, it would be a good practice to check that the amounts array is empty when it is erc721 as amounts are ignored for ERC721 vaults.
