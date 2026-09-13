# [M] owner can call the setNft function and set the nft to address(0).

## Summary
Severity: Medium
Reporter: dopeflamingo
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Type: audit-issue

## Details
# owner can call the setNft function and set the nft to address(0).

## Summary
The owner can call the setNft function and set the nft to an address(0) to stop minting of any nfts meaning users won't get any NFTs  minted everytime a user calls the mint function.

## Vulnerability Detail
This leads to the ```mint``` function in the MeritDutchAuction.sol reverting everytime it is called to mint an NFT, since there is no check that the nft being set is of address(0). There is also no check to make sure that a MeritNFT exists before the function is called, causing a revert everytime. This occurs whilst the price of the NFT is going down due to the nature of a dutch auction whilst the owner hasn't set a MeritNFT causing them to earn less funds than they could have got. 

## Impact
This leads to the owner having less funds as they didn't set a valid NFT in time or they didn't even set a valid NFT at all causing all transactions sent to the auction they started to revert. 

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96

## Tool used

Manual Review, Foundry

## Recommendation

add a require statement in ```MeritDutchAuction#setNFT```. ```require(nft_ != address(0));```. Also maybe add a check that the meritNFT exists in the ```mint``` function. So the owner can set a meritNFT in the meantime.
