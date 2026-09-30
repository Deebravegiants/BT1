# [H] H-4 Unsynchronized positions in NonFungiblePositionManager and

## Summary
Severity: High
Contest weight: 0.3442
Dataset id: 2855
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If FarmingCenter._updatePosition reverts internally, NonFungiblePositionManager ignores that revert here: NonfungiblePositionManager.sol#L369 leading to unsynchronized positions between the actual position and the farming position. The _updatePosition function consists of sequential calls to the exitFarming and enterFarming functions within the AlgebraEternalFarming contract FarmingCenter.sol#L94. While the exitFarming function does not possess explicit revert statements, the enterFarming function can revert here: AlgebraEternalFarming.sol#L385. These reverts prevent the creation of farming positions in detached or deactivated farmings. Consequently, if a pool is detached, every call to NonFungiblePositionManager.decreaseLiquidity will revert within the FarmingCenter._updatePosition function. As a result, the actual liquidity of the position in the pool will decrease, but the liquidity in the farming position will remain unchanged, allowing the tokenId owner to continue collecting higher rewards than deserved. Furthermore, this vulnerability can be exploited by users who can find a way to manually detach the pool from its incentive. Consider the following scenario:
• The exploiter obtains a flashloan from an external project
• The exploiter mints a position in the pool using loaned tokens and enters farming
• The exploiter detaches the pool
• The exploiter decreases liquidity of the position to the minimum possible causing desynchronization in AlgebraEternalFarming which retains the liquidity of the flashloaned tokens.
• The exploiter repays the flashloan
In this scenario, the exploiter can collect rewards without maintaining an actual position.

## Recommendation
We recommend implementing the forced exit from the farming position in cases when a revert occurs within the call of NonFungiblePositionManager here: NonfungiblePositionManager.sol#L369, if feasible, to prevent unsynchronized farming positions.
