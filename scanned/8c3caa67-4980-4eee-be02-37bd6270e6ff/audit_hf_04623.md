# [M] Incorrect logic causes that SequencerVaults to not behave as expected when relocking or claiming rewards.

## Summary
Severity: Medium
Contest weight: 0.7422
Dataset id: 22228
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A logic error exists in SequencerVault.updateDeposits() where rewards are not processed according to the function's documented behavior. According to the function in-line comments below, the comment `(set 0 to skip reward claiming)` indicates that when minRewards=0, the function should skip claiming but still process re-locking of rewards.

```solidity
//SequencerVault.sol
/**
 * @notice Updates the deposit and reward accounting for this vault
 * @dev will only pay out rewards if the vault is net positive when accounting for lost deposits
 * @param _minRewards min amount of rewards to relock/claim (set 0 to skip reward claiming) --> @audit
 * @param _l2Gas L2 gasLimit for bridging rewards
 * @return the current total deposits in this vault
 * @return the operator rewards earned by this vault since the last update
 * @return the rewards that were claimed in this update
 */
 function updateDeposits(
        uint256 _minRewards,
        uint32 _l2Gas
    ) external payable onlyVaultController returns (uint256, uint256, uint256) {
 // logic
}
```
However, the actual implementation:
```solidity
//SequencerVault.sol
function updateDeposits(
    uint256 _minRewards,
    uint32 _l2Gas
) external payable onlyVaultController returns (uint256, uint256, uint256) {
    uint256 principal = getPrincipalDeposits();
    uint256 rewards = getRewards();
    uint256 totalDeposits = principal + rewards;

    // ... code

    // Incorrectly skips all reward processing if minRewards=0
    if (_minRewards != 0 && rewards >= _minRewards) {
        if (
            (principal + rewards) <= vaultController.getVaultDepositMax() &&
            exitDelayEndTime == 0
        ) {
            lockingPool.relock(seqId, 0, true);
        } else {
            lockingPool.withdrawRewards{value: msg.value}(seqId, _l2Gas);
            trackedTotalDeposits -= SafeCastUpgradeable.toUint128(rewards);
            totalDeposits -= rewards;
            claimedRewards = rewards;
        }
    }
    // @audit No else block to handle relocking when minRewards=0

   // code..
    return (totalDeposits, opRewards, claimedRewards);
}
```

The implementation diverges from intended behavior:

When `minRewards=0`:
Expected: Skip claiming but process relocking
Actual: Skips all reward processing

When `minRewards == 0`, rewards are neither relocked nor claimed. This effectively leads to stuck rewards in `MetisLockingPool` until the sequencer is active.

## Proof of Concept
Add the following to `l1-strategy.test.ts`

```solidity
 const setupSequencerWithRewards = async () => {
    const { strategy, metisLockingPool, token, accounts } = await loadFixture(deployFixture)

    // Setup vault and deposit initial amount
    await strategy.addVault('0x5555', accounts[1], accounts[2])
    const vaults = await strategy.getVaults()
    const vault0 = await ethers.getContractAt('SequencerVault', vaults[0])

    await strategy.deposit(toEther(500))

    await strategy.depositQueuedTokens([0], [toEther(500)])
    assert.equal(fromEther(await vault0.getPrincipalDeposits()), 500)
    assert.equal(fromEther(await vault0.getTotalDeposits()), 500)

    // Add rewards to sequencer
    await metisLockingPool.addReward(1, toEther(50))
    assert.equal(fromEther(await vault0.getTotalDeposits()), 550)

    return { strategy, vault0, metisLockingPool }
  }

  it('rewards not processed when minRewardsToClaim is 0', async () => {
    const { strategy, vault0, metisLockingPool } = await setupSequencerWithRewards()

    // Set minRewardsToClaim to 0
    await strategy.setMinRewardsToClaim(0)

    const rewardsBefore = await vault0.getRewards()
    assert.equal(fromEther(rewardsBefore), 50)

    // Update deposits
    await strategy.updateDeposits(0, 0)

    // Rewards should be relocked but aren't
    const rewardsAfter = await vault0.getRewards()
    assert.equal(fromEther(rewardsAfter), 50)
  })
```

## Recommendation
Consider updating the current logic regarding reward management:
- rewards should be claimed when `minRewards > 0` && rewards exceed the minimum threshold!
- rewards should be relocked when `minRewards == 0`
