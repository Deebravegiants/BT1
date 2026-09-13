# [M] Auction admin can rig the auction by minting NFT for free for themselves without initial capital requirements.

## Summary
Severity: Medium
Reporter: thekmj
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Auction admin can rig the auction by minting NFT for free for themselves without initial capital requirements.

## Summary

The `MeritDutchAuction` contract is intended to sell sequentially-numbered NFTs, which specifications are defined in the `MeritNFT` contract. The admin rights of this contract, however, is stated to be restricted.

We identified a possible vector where the admin can rig the auction by buying themselves NFT for zero cost. This opens up attacks such as forcing the buyer to get NFTs that they did not intend. This attack does not require any initial capital for the admin to perform.

## Vulnerability Detail

An admin Bob can perform the following transaction to mint arbitrary number of NFTs for free:
- Bob flash-loans large amount of funds from, for example, Euler Finance ETH pool, Uniswap, or Balancer Vaults.
- Bob buys himself NFTs using said funds.
- As the admin, Bob withdraws proceeds from his own auction.
- Bob returns the flash-borrowed funds.

Bob is technically limited to 4 NFTs, but he can create arbitrary number of wallets to bypass the limit.

This opens up possibilities for Bob to rig the auction *against* Alice as follow:
- Bob is the admin of an ongoing auction.
- Alice wants to buy NFT 1, since it's the best NFT.
- Alice makes the transaction, calls `mint(1)`, and (tries to) buy NFT 1.
- Bob forces Alice to buy NFT numbered, say, 5, by front-running Alice with the given attack.
- Alice's transaction goes through, however she is given NFT 5 instead of the high-valued NFT 1 as she wanted.

Bob has forced Alice to buy NFT 5, while in reality she wants to buy NFT 1. Bob needed no initial capital requirements

## Impact

Admin can buy arbitrary NFT for free. They can also rig the auction in favor of certain participants, forcing others to buy different lesser-valued NFTs than they intended.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179

## Tool used

Manual Review

## Recommendation

Force a withdrawal timelock on the admin, preventing the admin from using the same funds to buy multiple NFTs. Or at least don't allow withdrawing twice within the same transaction.

Note that disallowing admin to claim proceeds before auction ends will not completely solve the issue, as admins can still perform this attack after the auction ends, since NFTs can still be sold then.
