# [H] setWeight() Logic error

## Summary
Severity: High
Chain: Smart contract
Component: 2023-05-maia
Published: 2023-07-05
Source: https://github.com/code-423n4/2023-05-maia-findings/issues/766
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-05-maia/blob/54a45beb1428d85999da3f721f923cbf36ee3d35/src/ulysses-amm/UlyssesPool.sol#L223


# Vulnerability details

## Impact
Logic error

## Proof of Concept
`setWeight()`Used to set the new weight
The code is as follows:
```solidity
    function setWeight(uint256 poolId, uint8 weight) external nonReentrant onlyOwner {
        if (weight == 0) revert InvalidWeight();

        uint256 poolIndex = destinations[poolId];

        if (poolIndex == 0) revert NotUlyssesLP();

        uint256 oldRebalancingFee;

        for (uint256 i = 1; i < bandwidthStateList.length; i++) {
            uint256 targetBandwidth = totalSupply.mulDiv(bandwidthStateList[i].weight, totalWeights);

            oldRebalancingFee += _calculateRebalancingFee(bandwidthStateList[i].bandwidth, targetBandwidth, false);
        }

        uint256 oldTotalWeights = totalWeights;
        uint256 weightsWithoutPool = oldTotalWeights - bandwidthStateList[poolIndex].weight;
        uint256 newTotalWeights = weightsWithoutPool + weight;
        totalWeights = newTotalWeights;

        if (totalWeights > MAX_TOTAL_WEIGHT || oldTotalWeights == newTotalWeights) {
            revert InvalidWeight();
        }

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-maia-findings/issues/766_
