# [M] Uninitialized owner can lead to owner being address(0)

## Summary
Severity: Medium
Reporter: 0xMAKEOUTHILL
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L5
Type: audit-issue

## Details
# Uninitialized owner can lead to owner being address(0)

## Summary
Uninitialized owner can lead to owner being address(0)

## Vulnerability Detail
OZ's ''Ownable" now requires explicitly to set the owner of the contract in the constructor

constructor(address initialOwner) {
     _transferOwnership(initialOwner);
 }

Ownable now doesn't automatically set the owner to the address that deployed the contract.

## Impact
Owner can be address(0) making the functions which use the onlyOwner modifier useless, 

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L5

## Tool used
Manual Review

## Recommendation
Init the owner in the constructor
