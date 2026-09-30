# [?] fix: prevent overflow in minDepositBlockDistance and maxDepositsPerBlock during module update

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2024-08-30
Source: https://github.com/lidofinance/core/commit/da704b8929d6c4a7c04a0bf814c21695198d94f4
Type: security-commit

## Details
fix: prevent overflow in minDepositBlockDistance and maxDepositsPerBlock during module update

Ackee L1: Overflow on type casting.
In the staking router, ensure that the new values for minDepositBlockDistance
and maxDepositsPerBlock are checked for potential overflow during module updates to avoid issues.

## Patch
### contracts/0.8.9/StakingRouter.sol
```diff
@@ -69,6 +69,7 @@ contract StakingRouter is AccessControlEnumerable, BeaconChainDepositor, Version
     error UnrecoverableModuleError();
     error InvalidPriorityExitShareThreshold();
     error InvalidMinDepositBlockDistance();
+    error InvalidMaxDepositPerBlockValue();
 
     enum StakingModuleStatus {
         Active, // deposits and rewards allowed
@@ -337,7 +338,8 @@ contract StakingRouter is AccessControlEnumerable, BeaconChainDepositor, Version
         if (_priorityExitShareThreshold > TOTAL_BASIS_POINTS) revert InvalidPriorityExitShareThreshold();
         if (_stakeShareLimit > _priorityExitShareThreshold) revert InvalidPriorityExitShareThreshold();
         if (_stakingModuleFee + _treasuryFee > TOTAL_BASIS_POINTS) revert InvalidFeeSum();
-        if (_minDepositBlockDistance == 0) revert InvalidMinDepositBlockDistance();
+        if (_minDepositBlockDistance == 0 || _minDepositBlockDistance > type(uint64).max) revert InvalidMinDepositBlockDistance();
+        if (_maxDepositsPerBlock > type(uint64).max) revert InvalidMaxDepositPerBlockValue();
 
         stakingModule.stakeShareLimit = uint16(_stakeShareLimit);
         stakingModule.priorityExitShareThreshold = uint16(_priorityExitShareThreshold);
```

### test/0.8.9/stakingRouter/stakingRouter.module-management.test.ts
```diff
@@ -14,6 +14,8 @@ import { StakingRouterLibraryAddresses } from "typechain-types/factories/contrac
 
 import { certainAddress, getNextBlock, proxify, randomString } from "lib";
 
+const UINT64_MAX = 2n ** 64n - 1n;
+
 describe("StakingRouter:module-management", () => {
   let deployer: HardhatEthersSigner;
   let admin: HardhatEthersSigner;
@@ -383,6 +385,58 @@ describe("StakingRouter:module-management", () => {
       ).to.be.revertedWithCustomError(stakingRouter, "InvalidMinDepositBlockDistance");
     });
 
+    it("Reverts if the new deposit block distance is great then uint64 max", async () => {
+      await stakingRouter.updateStakingModule(
+        ID,
+        NEW_STAKE_SHARE_LIMIT,
+        NEW_PRIORITY_EXIT_SHARE_THRESHOLD,
+        NEW_MODULE_FEE,
+        NEW_TREASURY_FEE,
+        NEW_MAX_DEPOSITS_PER_BLOCK,
+        UINT64_MAX,
+      );
+
+      expect((await stakingRouter.getStakingModule(ID)).minDepositBlockDistance).to.be.equal(UINT64_MAX);
+
+      await expect(
+        stakingRouter.updateStakingModule(
+          ID,
+          NEW_STAKE_SHARE_LIMIT,
+          NEW_PRIORITY_EXIT_SHARE_THRESHOLD,
+          NEW_MODULE_FEE,
+          NEW_TREASURY_FEE,
+          NEW_MAX_DEPOSITS_PER_BLOCK,
+          UINT64_MAX + 1n,
+        ),
+      ).to.be.revertedWithCustomError(stakingRouter, "InvalidMinDepositBlockDistance");
+    });
+
+    it("Reverts if the new max deposits per block is great then uint64 max", async () => {
+      await stakingRouter.updateStakingModule(
+        ID,
+        NEW_STAKE_SHARE_LIMIT,
+        NEW_PRIORITY_EXIT_SHARE_THRESHOLD,
+        NEW_MODULE_FEE,
+        NEW_TREASURY_FEE,
+        UINT64_MAX,
+        NEW_MIN_DEPOSIT_BLOCK_DISTANCE,
+      );
+
+      expect((await stakingRouter.getStakingModule(ID)).maxDepositsPerBlock).to.be.equal(UINT64_MAX);
+
+      await expect(
+        stakingRouter.updateStakingModule(
+          ID,
+          NEW_STAKE_SHARE_LIMIT,
+          NEW_PRIORITY_EXIT_SHARE_THRESHOLD,
+          NEW_MODULE_FEE,
+          NEW_TREASURY_FEE,
+          UINT64_MAX + 1n,
+          NEW_MIN_DEPOSIT_BLOCK_DISTANCE,
+        ),
+      ).to.be.revertedWithCustomError(stakingRouter, "InvalidMaxDepositPerBlockValue");
+    });
+
     it("Reverts if the sum of the new module and treasury fees is greater than 100%", async () => {
       const NEW_MODULE_FEE_INVALID = 100_01n - TREASURY_FEE;
 
```
