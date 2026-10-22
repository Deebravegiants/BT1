# [H] `setWeight` Logic error

## Summary
Severity: High
Contest weight: 0.8459
Dataset id: 18570
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logic error in the setWeight function that updates a pool's weight and redistributes bandwidth among all pools. The root cause is an incorrect conditional and arithmetic direction: the code checks if oldTotalWeights > newTotalWeights but the branch is intended for weight increases, and the mulDivUp call swaps the old and new total weight arguments, causing the new bandwidth to be calculated with the wrong divisor. In addition, the leftoverBandwidth variable is updated with an incorrect sign and distribution logic, so when weight is increased or decreased the leftover amount is either not allocated or is allocated to the wrong pool. An attacker (or the contract owner) can invoke setWeight with a crafted weight value, causing the contract to mis‑record bandwidth for pools, which leads to users receiving less bandwidth than expected, rewards being under‑paid, or in extreme cases bandwidth values becoming zero. The impact is a breach of the protocol's accounting guarantees: the total bandwidth no longer matches the sum of individual pool allocations, breaking the economic model and potentially allowing loss of funds or unfair advantage. The bug manifests whenever setWeight is called, especially when the new weight is higher than the previous one, because the faulty branch is taken. All pools, their owners, and any users who rely on correct bandwidth calculations are affected. The issue was discovered during a manual audit by Code4rena, where the auditor noticed that the conditional direction and the mulDivUp parameters did not align with the intended rebalancing formula. The problem is subtle because the arithmetic operations appear valid and the code compiles without errors, making the misallocation easy to miss in testing. To fix the issue, the conditional should be changed to correctly detect weight increases, the mulDivUp arguments must be swapped to use newTotalWeights as the numerator and oldTotalWeights as the denominator, and the leftoverBandwidth redistribution loop must be rewritten to ensure the exact leftover amount is allocated to the appropriate pool without overflow or loss. In conceptual terms the bug belongs to the class of rebalancing or proportional allocation errors where rounding and sign mistakes cause accounting drift.

## Proof of Concept
`setWeight()` is used to set the new weight. The code is as follows:
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

        uint256 leftOverBandwidth;

        BandwidthState storage poolState = bandwidthStateList[poolIndex];
        poolState.weight = weight;
        if (oldTotalWeights < newTotalWeights) {
            for (uint256 i = 1; i < bandwidthStateList.length;) {
                if (i != poolIndex) {
                    uint256 oldBandwidth = bandwidthStateList[i].bandwidth;
                    if (oldBandwidth > 0) {
                        bandwidthStateList[i].bandwidth =
                            oldBandwidth.mulDivUp(oldTotalWeights, newTotalWeights).toUint248();
                        leftOverBandwidth += oldBandwidth - bandwidthStateList[i].bandwidth;
                    }
                }

                unchecked {
                    ++i;
                }
            }
            poolState.bandwidth += leftOverBandwidth.toUint248();
        } else {
            uint256 oldBandwidth = poolState.bandwidth;
            if (oldBandwidth > 0) {
                poolState.bandwidth = oldBandwidth.mulDivUp(newTotalWeights, oldTotalWeights).toUint248();

                leftOverBandwidth += oldBandwidth - poolState.bandwidth;
            }

            for (uint256 i = 1; i < bandwidthStateList.length;) {
              
                if (i != poolIndex) {
                     if (i == bandwidthStateList.length - 1) {
                         bandwidthStateList[i].bandwidth += leftOverBandwidth.toUint248();
                     } else if (leftOverBandwidth > 0) {
                         bandwidthStateList[i].bandwidth +=
                            leftOverBandwidth.mulDiv(bandwidthStateList[i].weight, weightsWithoutPool).toUint248();
                     }
                }

                unchecked {
                    ++i;
                }
            }
        }
```
There are several problems with the above code:

1. `if (oldTotalWeights > newTotalWeights)` should be changed to `if (oldTotalWeights < newTotalWeights)` because the logic inside of the `if` is to calculate the case of increasing `weight`.
2. `poolState.bandwidth = oldBandwidth.mulDivUp(oldTotalWeights , newTotalWeights).toUint248();` should be modified to `poolState.bandwidth = oldBandwidth.mulDivUp(newTotalWeights, oldTotalWeights).toUint248();` because this calculates with the extra number.
3. `leftOverBandwidth` has a problem with the processing logic.

## Recommendation
```solidity
function setWeight(uint256 poolId, uint8 weight) external nonReentrant onlyOwner {
    ...

        if (oldTotalWeights < newTotalWeights) {
            for (uint256 i = 1; i < bandwidthStateList.length;) {
                if (i != poolIndex) {
                    uint256 oldBandwidth = bandwidthStateList[i].bandwidth;
                    if (oldBandwidth > 0) {
                        bandwidthStateList[i].bandwidth =
                            oldBandwidth.mulDivUp(oldTotalWeights, newTotalWeights).toUint248();
                        leftOverBandwidth += oldBandwidth - bandwidthStateList[i].bandwidth;
                    }
                }

                unchecked {
                    ++i;
                }
            }
            poolState.bandwidth += leftOverBandwidth.toUint248();
        } else {
            uint256 oldBandwidth = poolState.bandwidth;
            if (oldBandwidth > 0) {
                poolState.bandwidth = oldBandwidth.mulDivUp(newTotalWeights, oldTotalWeights).toUint248();

                leftOverBandwidth += oldBandwidth - poolState.bandwidth;
            }

            uint256 currentGiveWidth = 0;
            uint256 currentGiveCount = 0;
            for (uint256 i = 1; i < bandwidthStateList.length;) {

                 if (i != poolIndex) {
                      if(currentGiveCount == bandwidthStateList.length - 2 - 1) { //last
                          bandwidthStateList[i].bandwidth += leftOverBandwidth - currentGiveWidth;
                     }
                      uint256 sharesWidth = leftOverBandwidth.mulDiv(bandwidthStateList[i].weight, weightsWithoutPool).toUint248();
                      bandwidthStateList[i].bandwidth += sharesWidth;
                      currentGiveWidth += sharesWidth;  
                      currentCount++;
                  }                

                unchecked {
                    ++i;
                }
            }
        }
    ...
```
