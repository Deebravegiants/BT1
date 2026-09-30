# [M] `Vault::unbondingActive` can be out of sync with Chainlink and `FundFlowController` bonding

## Summary
Severity: Medium
Contest weight: 0.6633
Dataset id: 21938
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
** Each vault has a call to query whether its currently in an unbonding period, `Vault::unbondingActive`:
```solidity
function unbondingActive() external view returns (bool) {
    return block.timestamp < stakeController.getClaimPeriodEndsAt(address(this));
}
```
Here the comparison is `<`.

However in the Chainlink [vault](https://etherscan.io/address/0xbc10f2e862ed4502144c7d632a3459f49dfcdb5e):
```solidity
function _inClaimPeriod(Staker storage staker) private view returns (bool) {
    if (staker.unbondingPeriodEndsAt == 0 || block.timestamp < staker.unbondingPeriodEndsAt) {
      return false;
    }

    return block.timestamp <= staker.claimPeriodEndsAt;
}
```

and `FundFlowController::claimPeriodActive` the comparison is `<=`:
```solidity
function claimPeriodActive() external view returns (bool) {
    uint256 claimPeriodStart = timeOfLastUpdateByGroup[curUnbondedVaultGroup] + unbondingPeriod;
    uint256 claimPeriodEnd = claimPeriodStart + claimPeriod;

    return block.timestamp >= claimPeriodStart && block.timestamp <= claimPeriodEnd;
}
```

Hence at `block.timestamp == staker.claimPeriodEndsAt` the `unbondingActive` call will give the incorrect answer.

** `Vault::unbondingActive` is used in `FundFlowController` to determine which total unbonded and withdrawal orders for upkeep. And also in `VaultControllerStrategy::withdraw`:
```solidity
function withdraw(uint256 _amount, bytes calldata _data) external onlyStakingPool {
    // @audit claimPeriodActive() does `<= claimPeriodEnd`
    if (!fundFlowController.claimPeriodActive() || _amount > totalUnbonded)
        revert InsufficientTokensUnbonded();

    // ...

    for (uint256 i = 0; i < vaultIds.length; ++i) {
        // ...

        // @audit unbondingActive() does `< claimPeriodEnd`
        if (deposits != 0 && vault.unbondingActive()) {
            if (toWithdraw > deposits) {
                vault.withdraw(deposits);
                unbondedRemaining -= deposits;
                toWithdraw -= deposits;
            } else if (deposits - toWithdraw > 0 && deposits - toWithdraw < minDeposits) {
                vault.withdraw(deposits);
                unbondedRemaining -= deposits;
                break;
            } else {
                vault.withdraw(toWithdraw);
                unbondedRemaining -= toWithdraw;
                break;
            }
        }
    }
```
Hence at `block.timestamp == staker.claimPeriodEndsAt` the withdraw would incorrectly not withdraw anything.

This also applies to `VaultControllerStrategy::_depositToVaults`:
```solidity
if (vault.unbondingActive()) {
    totalRebonded += deposits;
}
```
Where `totalRebonded`, and in turn `totalUnbonded` would be wrong. However that is much less impactful as the vault is just about to go out of claim period and thus void until `FundFlowController::performUpkeep` is called which resets `totalUnbonded`.

## Proof of Concept
** Test that can be added to `vault-controller-strategy.test.ts`:
```javascript
it('should perform withdrawal at claim period end' , async () => {
    const {accounts, adrs, strategy, token, stakingController, vaults, fundFlowController, updateVaultGroups } =
      await loadFixture(deployFixture)

    // Deposit into vaults
    await strategy.deposit(toEther(500), encodeVaults([]))
    assert.equal(fromEther(await token.balanceOf(adrs.stakingController)), 500)
    for (let i = 0; i < 5; i++) {
      assert.equal(fromEther(await stakingController.getStakerPrincipal(vaults[i])), 100)
    }
    assert.equal(Number((await strategy.globalVaultState())[3]), 5)

    await updateVaultGroups([0, 5, 10], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([1, 6, 11], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([2, 7], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([3, 8], 0)
    await time.increase(claimPeriod)
    await updateVaultGroups([4, 9], 100)

    const claimPeriodEnd = Number(await fundFlowController.timeOfLastUpdateByGroup(0)) + unbondingPeriod + claimPeriod

    const balanceBefore = await token.balanceOf(accounts[0])

    // set to claim period end
    await time.setNextBlockTimestamp(claimPeriodEnd)
    await strategy.withdraw(toEther(50), encodeVaults([0, 5]))

    const balanceAfter = await token.balanceOf(accounts[0])

    // nothing was withdrawn
    assert.equal(balanceAfter - balanceBefore, 0n)
})
```

## Recommendation
** Consider changing `<` to `<=`:
```diff
function unbondingActive() external view returns (bool) {
-   return block.timestamp < stakeController.getClaimPeriodEndsAt(address(this));
+   return block.timestamp <= stakeController.getClaimPeriodEndsAt(address(this));
}
```
