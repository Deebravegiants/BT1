# [M] currentStakeLimitdepletes faster in some adapters,

## Summary
Severity: Medium
Contest weight: 0.1865
Dataset id: 10036
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BaseLSTAdapterUpgradeable.prefundedDeposit(), the stake amount is capped to the currentStakeLimit. This is to prevent the buffer from being completely drained. // Update the stake limit state in the storage $.packedStakeLimitData.setStorageStakeLimitStruct(data.updatePrevStakeLimit(currentStakeLimit - stakeAmount)); Before the staking occur, its checks whether the stakeAmount exceed current stakeLimit, if not modify the new stake limit to currentStakeLimit - stakeAmount. The issue is, the actual amount going to be spent could possibly lower than the stakeAmount fd04b40530d79d98632d2bfa7/napier-uups-adapters/src/adapters/BaseLSTAdapterUpgradeable.sol#L157-L158 // Actual amount of ETH spent may be less than the requested amount. stakeAmount = _stake(stakeAmount); // stake amount can be 0 which means the stake limit that was updated previously does not account for the actual amount that we staked. I found one instance of adapters where this could possibly occur, kelp/RsETHAdapter.sol: Input stakeAmount modified to lower value if its greater than the stakeLimit of RsETHDeposit pool, With every prefundedDeposit call where excess WETH is left to stake, the stake limit will deplete faster.

## Recommendation
The _stake() method do returns the actual spent amount, therefore I suggest to update the staking limit after the staking has been done. /// INTERACT /// // Deposit into the yield source // Actual amount of ETH spent may be less than the requested amount. stakeAmount = _stake(stakeAmount); // stake amount can be 0 /// WRITE /// // Update the stake limit state in the storage $.packedStakeLimitData.setStorageStakeLimitStruct(data.updatePrevStakeLimit(currentStakeLimit - stakeAmount));
