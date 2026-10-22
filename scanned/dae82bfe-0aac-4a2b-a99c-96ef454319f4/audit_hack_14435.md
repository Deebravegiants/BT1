# [H] Inconsistency between protocol intention and Implementation

## Summary
Severity: High
Reporter: 0xKodak
Source: https://github.com/kodakr/henrykodak.github.io/blob/master/images/Screenshot%202023-07-13%20013757.png
Type: audit-issue

## Details
# Inconsistency between protocol intention and Implementation

## Summary
The protocol intends Minter role to be EOA & not the auction contract (Info verified via sponsor @feder.eth) ![ see proof](https://github.com/kodakr/henrykodak.github.io/blob/master/images/Screenshot%202023-07-13%20013757.png).
 Judging from this intention, the code implementation does not tally and will lead to a DOS to all users during auction (contract/ caller isn't minter role).


## Vulnerability Detail
The test script was unable to detect this because it correctly assigns the auction contract the minter role before testing. However this isn't the intended design ![see proof above](https://github.com/kodakr/henrykodak.github.io/blob/master/images/Screenshot%202023-07-13%20013757.png).

## Impact
If the MeritNFT ```constructor()``` assigns minter role to an EOA as intended or any address other than the auction's, there will be DOS to user as auction contract is unable to mint NFT

## Code Snippet
Address assignment
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L46C9-L55C6

Minting action
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156C8-L159C10


## Tool used

Manual Review

## Recommendation
1. The auction contract should be set as minter role in the NFT contract. OR
2. If the protocol strictly intends minter to be EOA, then there would be a redesign of the code implementation in the ```mint()``` of the auction contract.
