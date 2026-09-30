# [H] Reward restakingcreates unnecessary unbonding in edge cases

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23584
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The PolygonStrategy::restakeRewards() function is publicly callable by anyone, allowing rewards to be restaked immediately before the PolygonStrategy::unbond() function is called. In specific scenarios, this can cause the protocol to unnecessarily unbond principal funds when rewards would have been sufficient to satisfy withdrawal requests. The issue stems from how rewards are calculated in the unbond() function:

```solidity
// In PolygonStrategy::unbond()
uint256 deposits = vault.getTotalDeposits();
uint256 principalDeposits = vault.getPrincipalDeposits();
uint256 rewards = deposits - principalDeposits; //@audit this would be 0 if restakeRewards is called
just before,!
if (rewards >= toUnbondRemaining) {
    vault.withdrawRewards();
    toUnbondRemaining = 0;
} else {
    toUnbondRemaining -= rewards;
    uint256 vaultToUnbond = principalDeposits >= toUnbondRemaining
        ? toUnbondRemaining
        : principalDeposits;
    vault.unbond(vaultToUnbond);
    toUnbondRemaining -= vaultToUnbond;
    ++numVaultsUnbonded; //@audit this will be 1 more than necessary
}
```

Meanwhile, the PolygonStrategy::restakeRewards() function is publicly accessible:

```solidity
// In PolygonStrategy::restakeRewards()
function restakeRewards(uint256[] calldata _vaultIds) external {
    for (uint256 i = 0; i < _vaultIds.length; ++i) {
        vaults[_vaultIds[i]].restakeRewards();
    }
    emit RestakeRewards();
}
```

Impact: Consider a specific scenario:
- First eligible vault has sufficient rewards to cover an unbonding request completely
- Just before unbond() is called, Alice calls restakeRewards()
- When unbond() executes, it finds no rewards and must unbond principal instead
- This unnecessarily increments numVaultsUnbonding

In this scenario, queued token deposits will face denial of service.

## Proof of Concept
```javascript
describe.only('restakeRewards forces protocol to wait for withdrawal delay', async () => {
    it('should force protocol to wait for withdrawal delay', async () => {
        const { token, strategy, vaults, fundFlowController, withdrawalPool, validatorShare } =
            await loadFixture(deployFixture)
        await withdrawalPool.setTotalQueuedWithdrawals(toEther(960))
        assert.equal(await fundFlowController.shouldUnbondVaults(), true);
        // 1. Pre-condition: one validator can cover the amount to unbond with his rewards.
        await validatorShare.addReward(vaults[0].target, toEther(1000));
        // 2. User front-runs the unbondVaults transaction and restakes rewards for validators.
        await strategy.restakeRewards([0]);
        const totalQueuedBefore = await strategy.totalQueued();
        // 3. Protocol is forced to unbond and wait for withdrawal delay even though
        // it could obtain the funds after calling vault.withdrawRewards.
        await fundFlowController.unbondVaults()
        const totalQueuedAfter = await strategy.totalQueued();
        assert.equal(await fundFlowController.shouldUnbondVaults(), false)
        // 4. TotalQueued did not increase, meaning strategy could not withdraw any funds
        // and vault is unbending(it wouldn't be if it cover the funds with the rewards).
        assert.equal(totalQueuedBefore, totalQueuedAfter)
        assert.equal(await vaults[0].isUnbonding(), true)
    })
})
```

## Recommendation
Consider restricting access to restakeRewards in both the strategy and vault contracts.
