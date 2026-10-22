# [H] Lack of slippage control over NFT IDs can force buyers to buy lesser-valued NFTs than intended, for the same price as the originally intended one.

## Summary
Severity: High
Reporter: thekmj
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Lack of slippage control over NFT IDs can force buyers to buy lesser-valued NFTs than intended, for the same price as the originally intended one.

## Summary

The MeritDutchAuction contract is designed to sell sequentially-numbered NFTs, which specifications are defined in the MeritNFT contract. 

However, due to the lack of slippage control over NFT IDs itself, a buyer can, very realistically, be forced to buy a lesser valued NFT than they intended, for the same price.

We also show that, **the optimal buying strategy** for a user, given technical capabilities, **will definitely put another user at risk**.

## Vulnerability Detail

It is natural to think that, in an auction with decaying price, the lower-numbered NFTs are valued higher (e.g. NFT 1 is of more value than NFT 2). It is also natural that in any auction, participants will try to be the one who gets the special item for the lowest price possible.

Suppose a hyped NFT is put on sale. 
- Alice, Bob, Charlie, and Dave, are all looking to be the one who owns the "special" NFT 1.
- As soon as the auction begins, all of them sends a `mint(1)` transaction to buy the coveted NFT. 
- All of their transactions go through, however three of them gets the non-special NFTs **for the same price** as the special one. 

The impact is clear, three of them are forced to buy an NFT that they did not intend to.

Another possible scenario is as follow:
- Eve genuinely wants to buy NFT $N$.
- Eve does not buy it immediately, but rather wait until someone comes and attempts to buy NFT $N$.
   - **Note that this is Eve's optimal buying strategy. She does not intend to grief, but she gets a lower price by waiting due to the price decay.**
- Frank sends a transaction, and attempts to buy NFT $N$.
- Eve front-runs Frank, buying NFT $N$, forcing Frank to get NFT $N+1$.

Using this strategy, Eve was able to buy NFT $N$ at the best possible price. However, Frank is forced to buy NFT $N+1$, which he did not intend to, for the same price as Eve did.
 
## Impact

Due to NFT ID slippage, users may be forced to buy lesser-valued NFTs that they did not intend to, for the same price as the intended one.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169

## Tool used

Manual Review

## Recommendation

 Add an NFT ID slippage control to `mint()`, reverting if the user does not get the exact NFT they wish for. There are two ways for this:
- Let the user specify the starting NFT to mint as a function parameter.
- Let the user specify the exact NFTs IDs they want to buy.
