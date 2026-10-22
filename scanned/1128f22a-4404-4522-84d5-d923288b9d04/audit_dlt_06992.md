# [M] Extensive permissions for owner

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-12-forgotten-runiverse
Published: 2022-12-21
Source: https://github.com/code-423n4/2022-12-forgotten-runiverse-findings/issues/4
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/00a247e70de35d7a96d0ce03d66c0206b62e2f65/contracts/RuniverseLandMinter.sol#L358
https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/ea5fce62baeabf3f9d067ad747cee521d7be3a8a/contracts/RuniverseLand.sol#L195
https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/00a247e70de35d7a96d0ce03d66c0206b62e2f65/contracts/RuniverseLandMinter.sol#L513


# Vulnerability details

## Impact & Proof Of Concepts / Implications
Some privileged functions are often unavoidable in smart contracts. However, in these contracts, the privileges are (unnecessarily) very extensive and without checks on the smart contract side:

1. He can use `ownerMint` (or `ownerMintUsingTokenId`) to mint an arbitrary number of tokens. While these functions should be used for private minting, there is nothing restricting the owner from minting more than 10,924 plots and using the function later on to mint additional plots.
2. He can use `setVestingStart` / `setVestingEnd` / `setLastVestingGlobalId` to change the vesting configuration at any point. This can cause already vested tokens to suddenly become unvested (and therefore untransferable). Furthermore, there is no restriction on the parameters, so an owner could for instance set a vesting end that is 100 years in the future.
3. He can change the plots that are available per size at any time with `setPlotsAvailablePerSize`. Therefore, a user might think that he buys a rare plot size, but the plot size becomes very common afterwards, destroying the value of his NFT.

Therefore, the user currently has to trust the owner that he does not perform any of the previously described actions.

## Recommended Mitigation Steps
1. Only allow the owner to mint up to 10,924 plots and only allow it before the other phases have started (mintlist / claimlist / public sale).
2. Remove these functions, these should be immutable parameters such that a user can be sure that his vesting date never changes.
3. Remove this function, this should be immutable such that the rarities of NFTs cannot be changed arbitarily.
