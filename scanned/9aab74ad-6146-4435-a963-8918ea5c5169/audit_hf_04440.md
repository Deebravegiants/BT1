# [H] Attacker can potentially inflate total deposit room in vault group to near infinity

## Summary
Severity: High
Contest weight: 0.5009
Dataset id: 21931
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** The `VaultControllerStrategy::deposit` function increases `totalDepositRoom` based on the difference between `maxDeposits` (from Chainlink) and `vaultMaxDeposits`, but fails to update `vaultMaxDeposits` afterwards. As a result, on every deposit, vault group deposit room increases by `maxDeposits - vaultMaxDeposits`, regardless of the actual deposit amount.

Furthermore, the `StakingPool` contract, which interacts with `VaultControllerStrategy`, has a public `depositLiquidity` function that can be called by any user. This function uses the current balance of the `StakingPool` contract for deposits, which can be manipulated by transferring small amounts of tokens directly to the contract.

The combination of these issues could allow a malicious actor to:
- Manipulate the deposit process by calling depositLiquidity in StakingPool with carefully crafted data after transferring a small amount of tokens to the contract.
- Artificially inflate `totalDepositRoom` in VaultControllerStrategy by repeatedly triggering the deposit function.

Note that this attack vector is possible whenever Chainlink increases its vault limits.

** Vault group total deposit room can be increased by attacker to near infinity by repeatedly calling deposits. This has 2 severe side-effects

- Unused vaults will never see any deposits even when vaults with ids less than deposit index are full
- Since withdrawals increase deposit room continuously, it is likely that a repeated attack, in the extreme case, can cause an deposit room overflow and thus block all withdrawals.

## Proof of Concept
**
```typescript
it('inflate deposit room in vault groups to infinity', async () => {
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

    const [, totalDepRoomBefore] = await strategy.vaultGroups(1)
    await stakingController.setDepositLimits(toEther(10), toEther(120))
    await stakingPool.deposit(accounts[0], 1 /*dust amount*/, [encodeVaults([0, 1, 2, 3, 4])])
    const [, totalDepRoomAfterFirstDeposit] = await strategy.vaultGroups(0)

    //@audit after first deposit, deposit room increases to 20 ether
    assert.equal(fromEther(totalDepRoomAfterFirstDeposit), 20)
    await stakingPool.deposit(accounts[0], 1 /*dust amount*/, [encodeVaults([4])])

    //@audit after first deposit, deposit room increases to 40 ether
    const [, totalDepRoomAfterSecondDeposit] = await strategy.vaultGroups(0)
    assert.equal(fromEther(totalDepRoomAfterSecondDeposit), 40)

    //@audit this can theoretically increase to infinity - disrupting the deposit logic
})
```

## Recommendation
** Update vaultMaxDeposits once all vault group total deposit rooms are updated.
