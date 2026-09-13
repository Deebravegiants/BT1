# [M] Auction House can set vault to existing vault and lock buyers out of thier funds

## Summary
Severity: Medium
Reporter: kiki_dev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L207-L208
Type: audit-issue

## Details
# Auction House can set vault to existing vault and lock buyers out of thier funds

## Summary
 auction admin can set the vault address to an exisitng vault that they own and steal all the users deposits. In `AuctionHouse.vy` there is a function `set_vault` that allows the creator of that auction to change the address of the vault. currently the only restriction is that the vault isnt address 0. A auction admin can set the vault address to an exisitng vault that they own and steal all the users deposits.

As you can see in the link below the only checks in `registar deposit` are to see if the token exist and that the auction house is a registared depositor. Both of these will be true in this attack.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L207-L208

As you can see in the link below in order to liquidate and get funds back the msg.sender needs to be the owner of the tokenId at the NFT address. In this attack the victim will not be the owner and will not have access to liquidating the funds.

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L328

 However the attacker will be able to liquidate all funds deposited by the victim to themselves. 

## Vulnerability Detail
For example:

Alice creates a auction that only she knows about. 10 NFT's to be sold
Alice wins each aution for next to nothing because she is the only one participating.
Then Alice creates another Auction this time is advertised. 10NFT's to be sold
Alice sets the vault address to the existing vault
Bob Makes a bid on the first auction and wins for 10 WETH
10 WETH is deposited into the vault that alice created from her first vault
Bob is ready to liquidate and calls`liquidate()` however the call reverts becasue ` ERC721(NFT).ownerOf(_token_id)` points to Alices address, since NFT is refering to the first set of NFT' from the first auction that Alice owns. 
Alice can now call liquidate and becasue she owns 100% of the shares for that tokenID she can withdraw all of Bob's avaible funds. 

Alice can do this for every person that buys an nft from the second auction.  

## Impact
Auction owner can steal all of the users deposits. 

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/AuctionHouse.vy#L300
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L207-L208
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L328

## Tool used

Manual Review

## Recommendation
Dont let vault to set to an existing vault. This can be done by placing a check in side of `set_vault` or can be done by putting a check inside of `registar_deposit` that checks that the just minted NFT is the same address as the one that is tied to that Vault.
