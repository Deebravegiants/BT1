# [M] mujee- revokeRole() function does not revoke MINTER_ROLE or URI_SETTER roles

## Summary
Severity: Medium
Reporter: mujee
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L54
Type: audit-issue

## Details
# mujee- revokeRole() function does not revoke MINTER_ROLE or URI_SETTER roles

mujee

medium

## Summary
The revokeRole() function inherited from AccessControl contract does not revoke roles because they haven't set the admin Role to the admin of the MeritNFT contract

## Vulnerability Detail
By using AccessControl the contract particularly is interested in more than one minter roles and is wanted to control their access when needed. Which includes that in future they can't stop any minter or the new Auction contract. By not assigning admin role to the admin, The NFT contract will never be able to revoke those he assigned roles to.

## Impact
The NFT contract will never have control on its minters in the future in which makes it to link to the only MeritDutchAuction contract which defines in its total mints of 1000 NFTs.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L54

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61

## Tool used
remix, foundry and Manual Review

## Recommendation

The recommendation is to set the admin role and assign it to some address that will have the access to revoke or grant role to any address.
