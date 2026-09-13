# [M] Missing zero address check for the NFT contract in setNFT.

## Summary
Severity: Medium
Reporter: 0xrobsol
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91C1-L96C6
Type: audit-issue

## Details
# Missing zero address check for the NFT contract in setNFT.

## Summary
The setNFT function in the given smart contract allows for the setting of a new NFT contract address. However, it lacks a critical check to prevent this address from being the zero address.

## Vulnerability Detail
The setNFT function, as currently implemented, allows the owner of the contract to set the address of the NFT contract that the main contract interacts with. This address is then used in various function calls throughout the main contract. The vulnerability arises because the function does not check whether the provided address is the zero address.

## Impact
If the NFT contract address is set to the zero address, any function calls to this address will fail. This could cause the main contract to be unable to perform crucial actions, such as minting tokens, and could result in loss of functionality. It could also be confusing and difficult to troubleshoot, as the failure would not be due to an error in the contract's code, but rather due to an invalid external address.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91C1-L96C6

## Tool used

Manual Review

## Recommendation
To mitigate this vulnerability, add a require statement to the setNFT function that checks if the provided address is the zero address, and reverts if it is.
