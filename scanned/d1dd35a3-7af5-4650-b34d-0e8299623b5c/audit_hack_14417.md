# [M] `MeritDutchAuction.sol` never initialized the `owner` for `Ownable.sol`

## Summary
Severity: Medium
Reporter: 0xdice91
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91
Type: audit-issue

## Details
# `MeritDutchAuction.sol` never initialized the `owner` for `Ownable.sol`

## Summary
OZ's Ownable.sol now requires the owner to be explicitly set rather than assuming msg.sender as before. Since the contract never calls the Ownable.sol constructor _owner is never set and is left as address(0). 
## Vulnerability Detail
```solidity
constructor(address initialOwner) {
        _transferOwnership(initialOwner);
    }
```
## Impact
Important functions protected by the onlyOwner() modifier become completely nonfunctional Example;

- [setNFT()](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91)
- [claimProceeds()](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172)

## Code Snippet
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/8b72e20e326078029b92d526ff5a44add2671df1/contracts/access/Ownable.sol#L38-L40

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172
## Tool used

Manual Review

## Recommendation
Call the Ownable.sol constructor to set the owner.
