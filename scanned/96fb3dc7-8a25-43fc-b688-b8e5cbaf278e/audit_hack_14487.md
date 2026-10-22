# [M] On minting, user is open to be front-runned, might resulting failed to mint

## Summary
Severity: Medium
Reporter: bitsurfer
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128
Type: audit-issue

## Details
# On minting, user is open to be front-runned, might resulting failed to mint

## Summary

On minting, user is open to be front-runned resulting failed to mint (on last id)

## Vulnerability Detail

In a typical Dutch auction, the price decreases over time, meaning participants who mint NFTs later can obtain them at a lower cost. In such cases, front-running may not provide a direct financial advantage to the front-runner.

However, it's important to consider that there can be various motivations behind front-running in different scenarios, even if it may not seem financially beneficial in the case of a Dutch auction. Some potential reasons for front-running a Dutch auction could include:

1. Competitive Advantage: By front-running and obtaining the desired NFTs before others, even at a higher price, the front-runner gains a competitive advantage over subsequent participants. This advantage could be based on factors such as rarity, exclusivity, or early access to unique features associated with the NFTs.

2. Speculative Trading: Some individuals may front-run the auction in the hope of profiting from the secondary market. They may believe that the value of the NFTs will increase significantly after the auction, regardless of the price paid during the auction.

3. Strategic Intent: The front-runner may have strategic reasons that go beyond immediate financial gains. For example, they may want to disrupt or manipulate the auction process, gain visibility and influence within the community, or simply enjoy the thrill of engaging in such activities.

It's important to note that these motivations may vary based on individual preferences, market conditions, and the specific context in which the Dutch auction is conducted. While front-running may not always offer direct financial advantages in a Dutch auction, individuals may still attempt it for other reasons related to their personal goals or the perceived opportunities in the NFT market.

In an edge case, the last minting around 10000 (- 4) token Id, user will not get any success mint.

## Impact

Common user can be front-runned and may failed to mint the nft

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128

## Tool used

Manual Review

## Recommendation

Multi-phase Auction or use some kind of randomization like randomized reveal window
