# [M] Staking rewards cannot be updated due to incorrect usage of `SafeERC20.safeApprove`

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-22
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/42
Type: hats-finding

## Details
**Github username:** @aviggiano
**Submission hash (on-chain):** 0xc73327d922227ef04633cf85d0cc9855f74499615581a3b5bf6f4c8064544332
**Severity:** medium severity

**Description:**
# Staking rewards cannot be updated due to incorrect usage of `SafeERC20.safeApprove`

In [4bc89a3051dd4db80415933425b7d51e3d9a9240](https://github.com/VMEX-finance/vmex/commit/4bc89a3051dd4db80415933425b7d51e3d9a9240), a commit change introduced another issue on the `ExternalRewardDistributor.beginStakingReward` function. 

By using `IERC20(underlying).safeApprove(stakingContract, type(uint).max);`, the manager will not be able to update staking rewards, as `safeApprove` [reverts](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/fcf35e5722847f5eadaaee052968a8a54d03622a/contracts/token/ERC20/utils/SafeERC20.sol#L45-L58) when changing allowance from non-zero to non-zero.

# Severity

Medium. Manager cannot update staking rewards.

# Proof of Concept

Please review the following test

```
TS_NODE_TRANSPILE_ONLY=1 hardhat test ./test-suites/test-aave/__setup.spec.ts  ./test-suites/test-aave/incentives/external/configure.spec.ts
```

```diff
diff --git a/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
index 8815218d..3f0164c7 100644
--- a/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
+++ b/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol
@@ -58,7 +58,8 @@ contract ExternalRewardDistributor is IExternalRewardsDistributor {
     require(!IAssetMappings(assetMappings).getAssetBorrowable(underlying), "Underlying cannot be borrowable for external rewards");
 
     stakingData[underlying][trancheId] = stakingContract;
-    IERC20(underlying).approve(stakingContract, type(uint).max);
+    // @audit-issue safeApprove reverts when changing allowance from non-zero to non-zero
+    IERC20(underlying).safeApprove(stakingContract, type(uint).max);
 
     //transfer all aToken's underlying to this contract and stake it
     uint256 amount = IERC20(aToken).totalSupply();
diff --git a/packages/contracts/test-suites/test-aave/incentives/external/configure.spec.ts b/packages/contracts/test-suites/test-aave/incentives/external/configure.spec.ts
index 46f29931..b0cab631 100644
--- a/packages/contracts/test-suites/test-aave/incentives/external/configure.spec.ts
+++ b/packages/contracts/test-suites/test-aave/incentives/external/configure.spec.ts
@@ -42,7 +42,7 @@ makeSuite('ExternalRewardsDistributor configure rewards', (testEnv: TestEnv) =>
     })
   });
 
-  it('Reject reward config not from manager', async () => {
+  it.only('Reject reward config not from manager', async () => {
     const { incentivesController, users, rewardTokens, incentivizedTokens, stakingContracts, incentUnderlying } = testEnv;
     await expect(
       incentivesController.connect(users[2].signer).beginStakingReward(
@@ -59,7 +59,7 @@ makeSuite('ExternalRewardsDistributor configure rewards', (testEnv: TestEnv) =>
       )).to.be.revertedWith('Only manager');
   });
 
-  it('Configure single asset reward', async () => {
+  it.only('Configure single asset reward', async () => {
     const { incentivesController, rewardTokens, incentUnderlying, stakingContracts, dai, usdc, incentivizedTokens } = testEnv;
     
     await incentivizedTokens[0].setTranche(0);
@@ -76,7 +76,7 @@ makeSuite('ExternalRewardsDistributor configure rewards', (testEnv: TestEnv) =>
     expect(assetData).equal(stakingContracts[0].address)
   })
 
-  it('Configure batch assets, fail on inconsistent parameter lengths', async () => {
+  it.only('Configure batch assets, fail on inconsistent parameter lengths', async () => {
     const { incentivesController, rewardTokens, incentUnderlying, stakingContracts, usdc, busd, aave, incentivizedTokens } = testEnv;
     await incentivizedTokens[1].setTranche(0); //technically they are already 0?
     await expect(
@@ -170,6 +170,74 @@ makeSuite('ExternalRewardsDistributor configure rewards', (testEnv: TestEnv) =>
     assetData = await incentivesController.getStakingContract(incentivizedTokens[0].address);
     expect(assetData).equal(stakingContracts[5].address)
   })
+  it.only('Should be able to remove staking reward and add it again', async () => {
+    const { incentivesController, rewardTokens, incentUnderlying, stakingContracts, dai, users, incentivizedTokens } = testEnv;
+    
+
+    await expect(incentivesController.beginStakingReward(
+      incentivizedTokens[0].address, 
+      stakingContracts[5].address
+    )).to.be.revertedWith("Cannot add staking reward for a token that already has staking");
+
+    await expect(incentivesController.beginStakingReward(
+      incentivizedTokens[0].address, 
+      stakingContracts[0].address
+    )).to.be.revertedWith("Cannot add staking reward for a token that already has staking");
+
+
+    // add some liquidity to the aToken via a deposit. 
+    const aToken = incentivizedTokens[0]
+    const asset = incentUnderlying[0]
+    const staking = stakingContracts[0]
+    const reward = rewardTokens[0]
+    const user = users[0]
+
+    console.log(" users 0 deposit 1000 of the asset (usdc) to aToken (incentivizedTokens[0])");
+    await asset.connect(user.signer).mint(100000);
+    await asset.connect(user.signer).approve(aToken.address, 1000);
+    await aToken.deposit(user.address, 1000);
+
+    increaseTime(50000)
+    await harvestAndUpdate(testEnv);
+    console.log("leaf nodes after user 0 deposits: ",testEnv.leafNodes)
+
+    console.log(" users 1 deposit 1000 of the asset (usdc) to aToken (incentivizedTokens[0])");
+    await asset.connect(users[1].signer).mint(100000);
+    await asset.connect(users[1].signer).approve(aToken.address, 1000);
+    await aToken.connect(users[1].signer).deposit(users[1].address, 1000);
+
+
+    increaseTime(50000)
+    await harvestAndUpdate(testEnv);
+    console.log("leaf nodes after user 1 deposits: ",testEnv.leafNodes)
+
+    let assetData = await incentivesController.getStakingContract(incentivizedTokens[0].address);
+    expect(assetData).equal(stakingContracts[0].address)
+
+    console.log("remove the current staking reward and change it to reward 5")
+    await incentivesController.removeStakingReward(
+      incentivizedTokens[0].address
+    );
+
+    await incentivesController.beginStakingReward(
+      incentivizedTokens[0].address, 
+      stakingContracts[5].address
+    );
+
+    console.log("@audit until this point, the test is the same as the previous one")
+    console.log("@audit now remove the staking reward and try to add again")
+
+    await incentivesController.removeStakingReward(
+      incentivizedTokens[0].address
+    );
+
+    console.log("@audit adding the same reward again will revert, since safeApprove does not allow approving from non-zero to non-zero")
+
+    expect(incentivesController.beginStakingReward(
+      incentivizedTokens[0].address, 
+      stakingContracts[5].address
+    )).to.be.revertedWith('SafeERC20: approve from non-zero to non-zero allowance');
+  })
   it('Calculate Merkle and claim rewards', async () => {
     const { incentivesController, incentivizedTokens, usdc, stakingContracts, incentUnderlying, users, rewardTokens, dai, leafNodes } = testEnv;
     const arr = leafNodes.map((i,ix) => {

```

# Recommendation

`SafeERC20.safeApprove` has been [deprecated](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/fcf35e5722847f5eadaaee052968a8a54d03622a/contracts/token/ERC20/utils/SafeERC20.sol#L39). Its usage is [discouraged](https://github.com/OpenZeppelin/openzeppelin-contracts/issues/2219). Do not use `SafeERC20.safeApprove`, but rather `SafeERC20.safeIncreaseAllowance`.

See a similar issue [here](https://github.com/code-423n4/2022-04-backd-findings/issues/180).
