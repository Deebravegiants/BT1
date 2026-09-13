# [M] mujee - grantRole() does not grant roles

## Summary
Severity: Medium
Reporter: mujee
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L54
Type: audit-issue

## Details
# mujee - grantRole() does not grant roles

mujee

medium

## Summary
The grantRole function inherited from AccessControl contract does not grant roles because they haven't set the admin Role to the admin of the MeritNFT contract

## Vulnerability Detail
By using AccessControl the contract particularly is interested in more than one minter roles. Which includes that in future they can relaunch the new Auction contract. But not assigning admin role to the admin the NFT contract will never be able to have more than one minter which restrict its supply.
## Impact
The NFT contract will never have more than 1000 NFTs and more than one minter or any new auction in the future.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L54

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61

## Tool used
remix, foundry and
Manual Review

## Recommendation

The recommendation is to set the admin role and assign it to some address that will have the access to revoke or grant role to any address.
