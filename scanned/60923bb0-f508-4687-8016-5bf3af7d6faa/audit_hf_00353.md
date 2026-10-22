# [M] LidoVault::vaultEndedWithdrawdoesn't take into

## Summary
Severity: Medium
Contest weight: 0.6714
Dataset id: 1720
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
experience slashing. This is expected on the protocol's side, as the impact would be lower income, but it is expected for the protocol to keep functioning as expected, from the contest README:
These incidents will decrease income from deposits to the Lido Liquid Staking protocol and could decrease the stETH balance. The contract must be operational after it, but it is acceptable for users to lose part of their income/deposit...
However, this isn't always preserved, let's take the following scenario. We have withdraws his cut of that profit, by calling LidoVault::withdraw. When doing so, withdrawnStakingEarningsInStakes gets updated to reflect the amount of withdrawn profit shares, but, this value is calculated after some profit. No more profit comes in, and the vault ends, as soon as it ends, before any withdrawals, the vault gets slashed with some amount. Now, when variable users come to withdraw their profit (slashing didn't remove the whole profit), totalEarnings will be calculated wrongly, as the following:
```solidity
uint256 totalEarnings = vaultEndingETHBalance.mulDiv(withdrawnStakingEarningsInStakes, vaultEndingStakesAmount) - totalProtocolFee + vaultEndedStakingEarnings;
```
As the used vaultEndingETHBalance and vaultEndingStakesAmount represent the amounts after slashing, while withdrawnStakingEarningsInStakes represents the withdrawn shares before slashing.
This results in wrong totalEarnings that also result in wrong stakingEarningsShare value for the VARIABLES users, stakingEarningsShare will be greater than the contract's balance, forcing funds to be stuck forever, as transferWithdrawnFunds will revert.
When calculating the total earned ETH in LidoVault::vaultEndedWithdraw, the protocol doesn't take into consideration the slashing that happened after the vault ended, especially when some VARIABLE users withdrew part of their profit while the vault is still ongoing. withdrawnStakingEarningsInStakes will be a misleading dit/2024-08-saffron-finance/blob/main/lido-fiv/contracts/LidoVault.sol#L775

## Proof of Concept
Add the following test in lido-fiv/test/1.LidoVault.test.ts:
```typescript
it("BUG - DOS, can't withdraw after Slashing", async () => {
    const { lidoVault, addr1, addr2, addr3 } = await loadFixture(deployLidoVaultFixture)
    const { lidoMock } = await setupMockLidoContracts(lidoVault)
    await lidoVault.connect(addr2).deposit(SIDE.VARIABLE, { value: parseEther('15') })
    await lidoVault.connect(addr3).deposit(SIDE.VARIABLE, { value: parseEther('15') })
    // Vault has started
    expect(await lidoVault.isStarted()).to.equal(true)
    // Half time passes
    const { duration, endTime } = await getTimeState(lidoVault)
    await time.increaseTo(endTime - duration / BigInt(2))
    // Lido rebasing, vault earns 100 ETH
    await lidoMock.addStakingEarningsForTargetETH(
        parseEther('1100'),
        await lidoVault.getAddress()
    )
    // User 2 withdraws their income (part of the above rebasing)
    await lidoVault.connect(addr2).withdraw(SIDE.VARIABLE)
    // Withdrawal was sent to Lido
    expect(
        (await lidoVault.getVariableToVaultOngoingWithdrawalRequestIds(addr2.address)).length
    ).to.equal(1)
    // `withdrawnStakingEarningsInStakes` is now > 0
    expect(await lidoVault.withdrawnStakingEarningsInStakes()).to.be.greaterThan(0)
    // End time passes
    await time.increaseTo(endTime + BIG_INT_ONE)
    // Vault is ended
    expect(await lidoVault.isEnded()).to.equal(true)
    // Lido slashes the vault
    await lidoMock.subtractStakingEarnings(parseEther('50'))
    // User 3 can't withdraw his income
    await expect(
        lidoVault.connect(addr3).finalizeVaultEndedWithdrawals(SIDE.VARIABLE)
    ).to.be.revertedWith('ETF')
})
```

## Recommendation
In LidoVault::vaultEndedWithdraw, when calculating the totalEarnings when a variable user is withdrawing, consider the income that was withdrawn before Lido slashing happens. Maybe have something like the following?
```solidity
totalEarnings = Math.min(totalEarnings, vaultEndingETHBalance);
```
