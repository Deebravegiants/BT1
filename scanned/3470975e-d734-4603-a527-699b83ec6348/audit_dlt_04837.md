# [M] Improper implementation of IERC2981 in ERC2981.sol

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/122
Type: sherlock-finding

## Details
cryptphi

medium

# Improper implementation of IERC2981 in ERC2981.sol

## Summary
ERC2981 contract inherits IERC2981 but does not implement the royaltyInfo() function

## Vulnerability Detail
The ERC2981 inherits both IERC165 and IERC2981, however does not implement the royaltyInfo() function to comply with the NFT Royalty Standard.

## Impact
Non-compliance to NFT Royalty Standard

## Code Snippet
https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/lib/ERC2981.sol#L7-L20

## Tool used

Manual Review

## Recommendation
Add the royaltyInfo() function to the contract.
