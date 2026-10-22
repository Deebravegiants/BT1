# [M] `setPlotsAvailablePerSize` does not work correctly

## Summary
Severity: Medium
Contest weight: 0.2228
Dataset id: 17248
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[contracts/RuniverseLandMinter.sol#L513](https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/00a247e70de35d7a96d0ce03d66c0206b62e2f65/contracts/RuniverseLandMinter.sol#L513)

The function `setPlotsAvailablePerSize` can be used for two things:

  1. Decreasing the number of plots that is available for a certain size
  2. Increase the number of plots that is available for a certain size

However, in both cases it can introduce errors that can brick parts of the contract. In case 1 where the number of plots is decreased, it is possible that the new number is smaller than `plotsMinted` for a specific ID. This will cause an underflow in `getAvailableLands`, which subtracts these values:
    
    plotsAvailableBySize[0] = plotsAvailablePerSize[0] - plotsMinted[0];
    plotsAvailableBySize[1] = plotsAvailablePerSize[1] - plotsMinted[1];
    plotsAvailableBySize[2] = plotsAvailablePerSize[2] - plotsMinted[2];
    plotsAvailableBySize[3] = plotsAvailablePerSize[3] - plotsMinted[3];
    plotsAvailableBySize[4] = plotsAvailablePerSize[4] - plotsMinted[4];

On the other hand, when the number of available plots per size is increased, the minting can fail. This can happen because the `MAX_SUPPLY` in `RuniverseLand` is set to 70000, which is also the sum of all `plotsAvailablePerSize` entries. When the sum of these entries is increased beyond 70000, some tokens cannot be minted, because the `MAX_SUPPLY` is already reached.

## Recommendation
Enforce that

  1. All entries are larger than `plotsMinted`
  2. The new entries sum up to 70000 (or to a number that is <= 70000 if decreasing the max supply should be allowed)

Lack of check to guarantee invariant.

Similarly to [`#10`](https://github.com/code-423n4/2022-12-forgotten-runiverse-findings/issues/10) and [`#11`](https://github.com/code-423n4/2022-12-forgotten-runiverse-findings/issues/11), the Warden has shown a way for an invariant to be broken based on configuration.

Because certain aspects of the codebase are using the invariants which can be bypassed as shown above, I agree with Medium Severity.

We updated the code with the next changes:  

  * We removed `setPlotsAvailablePerSize`

<https://github.com/bisonic-official/plot-contract/commit/ea8abd7faffde4218232e22ba5d8402e37d96878>
