# [H] DoS in unbonding when validator rewards fall below min amount threshold

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23585
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The unbond function in PolygonStrategy is vulnerable to DoS when small reward amounts are used to cover the remaining amount to withdraw.  
When `PolygonFundFlowController.unbondVaults` is called it passes the amount to withdraw/unbond to `PolygonStrategy.unbond`:

```solidity
function unbondVaults() external {
    ...
    uint256 toWithdraw = queuedWithdrawals - (queuedDeposits + validatorRemovalDeposits);
    @> strategy.unbond(toWithdraw);
    timeOfLastUnbond = uint64(block.timestamp);
}
```

The `unbond` function loops through validators, using their rewards to cover the withdrawal amount. If rewards are insufficient, it unbonds from the validator's principal deposits.

```solidity
function unbond(uint256 _toUnbond) external onlyFundFlowController {
    ...
    if (rewards >= toUnbondRemaining) {
        // @audit withdrawRewards could be below the threshold from ValidatorShares
        @> vault.withdrawRewards();
        toUnbondRemaining = 0;
    } else {
        toUnbondRemaining -= rewards;
        uint256 vaultToUnbond = principalDeposits >= toUnbondRemaining
            ? toUnbondRemaining
            : principalDeposits;
        @> vault.unbond(vaultToUnbond);
        toUnbondRemaining -= vaultToUnbond;
        ++numVaultsUnbonded;
    }
    ...
}
```

A common, though infrequent, scenario occurs when iteration leaves `toUnbondRemaining` with a small amount for the next validator. This amount may be coverable by the validator's rewards, but if those rewards are below the threshold in the `ValidatorShares` contract, the transaction will revert, causing a DoS in the unbond process.

**Example:**
1. Strategy has 3 validators.  
2. Validator 3 has accumulated 0.9 tokens in rewards.  
3. The system needs to unbond 30.5 tokens in total.  
4. Validators 1 and 2 cover 30 tokens with their unbonds.  
5. Validator 3 is expected to cover the remaining 0.5 tokens with its 0.9 rewards (`withdrawRewards` is triggered).  
6. The transaction reverts because 0.9 tokens is less than `minAmount` from `ValidatorShares`.

The current logic also allows a malicious user to DoS the unbond transaction due to the way rewards are calculated in the unbond function:

```solidity
uint256 deposits = vault.getTotalDeposits();
uint256 principalDeposits = vault.getPrincipalDeposits();
uint256 rewards = deposits - principalDeposits;
```

`getTotalDeposits` accounts for the current token balance in the `PolygonVault` contract. If the `toUnbondRemaining` and validator's rewards are less than the vault's minimum rewards, an attacker can front‑run the transaction and cause `unbond` to revert:

1. Attacker sends a dust amount to the `PolygonVault`, enough to cover `toUnbondRemaining` but `< 1e18` (minimum rewards).  
2. `rewards = deposits - principalDeposits >= toUnbondRemaining`.  
3. Vault will call `withdrawRewards` but the claim amount is `< 1e18` (trigger for the revert in `ValidatorShares`).  
4. Transaction reverts.

**Impact:** DoS in the unbonding process when small rewards (`< 1e18`) are needed to complete withdrawals, blocking the protocol's withdrawal flow.

## Proof of Concept
1. Adjust the `PolygonValidatorShareMock` to reflect the same behavior as `ValidatorShares` by adding a minimum amount requirement when withdrawing rewards.

```solidity
// PolygonValidatorShareMock
function withdrawRewardsPOL() external {
    uint256 rewards = liquidRewards[msg.sender];
    if (rewards == 0) revert NoRewards();
    + require(rewards >= 1e18, "Too small rewards amount");
    delete liquidRewards[msg.sender];
    stakeManager.withdraw(msg.sender, rewards);
}
```

2. Paste the following test in `polygon-fund-flow-controller.test.ts` and run `npx hardhat test`.

```typescript
// test/polygonStaking/polygon-fund-flow-controller.test.ts:
describe.only('DoS', async () => {
    it('will revert when withdrawRewards < 1e18', async () => {
        const { token, strategy, vaults, fundFlowController, withdrawalPool, validatorShare,
        validatorShare2, validatorShare3 } =,!
        await loadFixture(deployFixture)
        console.log("will print some stuff")
        // validator funds: [10, 20, 30]
        await withdrawalPool.setTotalQueuedWithdrawals(toEther(970.5));
        assert.equal(await fundFlowController.shouldUnbondVaults(), true);

        // 1. Pre-condition: validator acumulated dust rewards since last unbonding.
        await validatorShare3.addReward(vaults[2].target, toEther(0.9));
        // expect that vault 2 has rewards
        assert.equal(await vaults[2].getRewards(), toEther(0.9));
        // 2. Unbond:
        // Validator A will cover 10 with unbond
        // Validator B will cover 20 with unbond
        // Validator C will cover the remaining 0.5 with his 0.9 rewards.
        await expect(fundFlowController.unbondVaults()).to.be.revertedWith("Too small rewards amount");
    })
})
```

Output:

```
PolygonFundFlowController
DoS
will revert when withdrawRewards < 1e18 (800ms)
1 passing (800ms)
```

## Recommendation
Recommended Mitigation: In the `PolygonStrategy.unbond` check if the actual rewards that can be withdrawn from the `ValidatorShares` is greater than the min amount for claim (`1e18`) before calling `withdrawRewards`.

```diff
- if (rewards >= toUnbondRemaining) {
-     vault.withdrawRewards();
-     toUnbondRemaining = 0;
+ if (rewards >= toUnbondRemaining && vault.getRewards() >= vault.minAmount()) {
+     vault.withdrawRewards();
+     toUnbondRemaining = 0;
  } else {
+     if (toUnbondRemaining > rewards) {
+         toUnbondRemaining -= rewards;
+     }
-     toUnbondRemaining -= rewards;
      uint256 vaultToUnbond = principalDeposits >= toUnbondRemaining
          ? toUnbondRemaining
          : principalDeposits;
```
