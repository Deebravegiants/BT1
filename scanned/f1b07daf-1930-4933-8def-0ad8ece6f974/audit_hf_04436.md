# [H] Implicit assumption of sequentially filling of vaults in `CommunityVCS::getDepositChange` causes direct losses to stakers

## Summary
Severity: High
Contest weight: 0.7538
Dataset id: 21927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `getDepositChange` function in the CommunityVCS contract can lead to significant underreporting of the total balance in the protocol. The function is designed with an assumption that vaults are filled sequentially, but this assumption can easily be violated with withdrawals.

Vault ID's in a given `curUnbondedVaultGroup` are not sequential but separated by the `numVaultGroups` which is set to 5 for Community Vault Controller Strategy. If there is a full withdrawal at any index, the `getDepositChange` will stop including the deposits for all subsequent vaults.

The vulnerable code in CommunityVCS:

```solidity
function getDepositChange() public view override returns (int) {
    uint256 totalBalance = token.balanceOf(address(this));
    for (uint256 i = 0; i < vaults.length; ++i) {
        uint256 vaultDeposits = vaults[i].getTotalDeposits();
        if (vaultDeposits == 0) break;
        totalBalance += vaultDeposits;
    }
    return int(totalBalance) - int(totalDeposits);
}
```

This function stops counting at the first empty vault it encounters. When StakingPool calls `updateDeposits`, the incorrect change is then used to update the `totalStaked` value. This causes an accounting loss to the users as the `totalStaked` would artificially reduce, similar to what happens during slashing.

Total deposits of non-sequential vaults are not counted towards `totalBalance` if there is an empty vault with a lower index. This has a similar effect of slashing. Key effects are:
- `TotalStaked` on Staking Pool drops causing a direct loss to stakers
- Fee receivers do not accrue a fee

## Proof of Concept
Below POC shows that if the first vault is fully withdrawn, `getDepositChange` stops including the vault deposits for all the subsequent vaults.

```javascript
it(`sequential deposits assumption in Community VCS can be attacked`, async () => {
    const {
      accounts,
      adrs,
      token,
      rewardsController,
      stakingController,
      strategy,
      stakingPool,
      updateVaultGroups,
    } = await deployCommunityVaultFixture()

    await strategy.deposit(toEther(1200), encodeVaults([]))

    await updateVaultGroups([0, 5, 10], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([1, 6, 11], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([2, 7], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([3, 8], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([4, 9], 300)
    await time.increase(claimPeriod)
    await updateVaultGroups([0, 5, 10], 300)

    //@audit withdraw from the first vault
    await strategy.withdraw(toEther(100), encodeVaults([1]))

    let vaults = await strategy.getVaults()

    let totalDeposits = 0

    for (let i = 0; i < 15; i++) {
      let vault = await ethers.getContractAt('CommunityVault', vaults[i])
      totalDeposits += fromEther(await vault.getTotalDeposits())
    }

    console.log(`total deposits`, totalDeposits)
    assert.equal(totalDeposits, 1100) //@audit 1200 (deposit) - 100 (withdrawn)

    // const strategyTokenBalance = fromEther(await token.balanceOf(adrs.strategy))
    // console.log(`strategy token balance`, totalDepositsCalculated)
    const depositChange = fromEther(await strategy.getDepositChange())

    assert.equal(depositChange, -1000) //@audit This is equivalent to slashing
    //@audit -> deposit Change should be 0 at this point, instead it is -1000
    //@audit only the 0'th vault deposit is considered in the deposit change calculation
  })
```

## Recommendation
Consider using the base implementation for `getDepositChange`. With the current withdrawal logic, a sequential deposit assumption can be easily violated.
