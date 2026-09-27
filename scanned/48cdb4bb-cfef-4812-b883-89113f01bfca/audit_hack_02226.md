# [M] setPlotsAvailablePerSize does not work correctly

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/00a247e70de35d7a96d0ce03d66c0206b62e2f65/contracts/RuniverseLandMinter.sol#L513
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/00a247e70de35d7a96d0ce03d66c0206b62e2f65/contracts/RuniverseLandMinter.sol#L513


# Vulnerability details

## Impact
The function `setPlotsAvailablePerSize` can be used for two things:
1. Decreasing the number of plots that is available for a certain size
2. Increase the number of plots that is available for a certain size

However, in both cases it can introduce errors that can brick parts of the contract. In case 1 where the number of plots is decreased, it is possible that the new number is smaller than `plotsMinted` for a specific ID. This will cause an underflow in `getAvailableLands`, which subtracts these values:
```solidity
        plotsAvailableBySize[0] = plotsAvailablePerSize[0] - plotsMinted[0];
        plotsAvailableBySize[1] = plotsAvailablePerSize[1] - plotsMinted[1];
        plotsAvailableBySize[2] = plotsAvailablePerSize[2] - plotsMinted[2];
        plotsAvailableBySize[3] = plotsAvailablePerSize[3] - plotsMinted[3];
        plotsAvailableBySize[4] = plotsAvailablePerSize[4] - plotsMinted[4];
```

On the other hand, when the number of available plots per size is increased, the minting can fail. This can happen because the `MAX_SUPPLY` in `RuniverseLand` is set to 70000, which is also the sum of all `plotsAvailablePerSize` entries. When the sum of these entries is increased beyond 70000, some tokens cannot be minted, because the `MAX_SUPPLY` is already reached. 

## Proof Of Concept
`plotsAvailablePerSize[0]` is changed by the owner to 54500, all other entries are kept the same. Because more users prefer cheap plots, they buy all 54500 plots of size 8x8 and 15500 plots of size 16x16. However, this means that 70000 tokens are minted and no one can buy the 32x32 or 64x64, leading to a substantial financial loss for the protocol (because larger investors might have bought them later, but can no longer do so).

## Recommended Mitigation Steps
Enforce that
1. All entries are larger than `plotsMinted`
2. The new entries sum up to 70000 (or to a number that is <= 70000 if decreasing the max supply should be allowed)
