# [M] Attacker can deny users from depositing into priority pool by front-running call to StakingPool::depositLiquidity()

## Summary
Severity: Medium
Contest weight: 0.3097
Dataset id: 21936
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The `VaultControllerStrategy` contract is susceptible to a front-running attack that can prevent priority pool from depositing user funds into specific vaults of a strategy. The vulnerability lies in the `deposit` function, which uses a `globalState.groupDepositIndex` to track the current deposit state. An attacker can exploit this by front-running legitimate deposits by calling `depositLiquidity` that deposits unused deposits into a strategy.

The griefing attack works as follows:
1. Priority pool prepares a transaction to deposit funds, specifying a list of vault IDs.
2. An attacker observes this pending transaction in the mempool.
3. The attacker quickly submits their own transaction that uses unused staking pool deposits, using the same vault IDs but with a higher gas price.
4. The attacker's transaction is processed first, updating the `globalState.groupDepositIndex`
5. When the priority pool transaction is processed, it fails due to an `InvalidVaultIds` error, as the `globalState.groupDepositIndex` no longer matches the expected value.

** In certain scenarios, priority pool can be prevented from depositing user funds, effectively creating a denial of service condition for the deposit functionality. It is noteworthy that an attacker need not use his own funds to execute the attack but use the unused staking pool deposits (when available) to grief other depositors.

## Proof of Concept
**
```typescript
it('front-running deposit to change deposit index', async () => {
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
      vaults,
    } = await loadFixture(deployFixture)

    await token.transfer(await stakingPool.getAddress(), toEther(100)) //depositing to represent unused liquidity in staking pool
    //@audit front-run priority pool deposit
    await stakingPool.connect(signers[2]).depositLiquidity([encodeVaults([0, 1, 2, 3, 4])]) // anyone can deposit this

    //@audit actual deposit is DOSed as the group deposit index has changed
    await expect(
      priorityPool.connect(signers[2]).deposit(toEther(100), false, [encodeVaults([0, 1, 3, 4])])
    ).to.be.revertedWithCustomError(strategy, 'InvalidVaultIds()')
})
```

## Recommendation
** Consider one of the alternatives:
- Gate the `StakingPool::depositLiquidity` function to prevent unauthorized access
- Redesign the deposit mechanism to not rely on sequential vault IDs or a global deposit index. Instead, use a more robust method for managing deposits that is resistant to order manipulation.
