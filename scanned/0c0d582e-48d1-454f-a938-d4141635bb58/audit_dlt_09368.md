# [?] Fix permitBatchAndCall reentrancy attack (#1110)

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2024-11-19
Source: https://github.com/balancer/balancer-v3-monorepo/commit/a318afe5edf1b90e68a89feb3f0a7930a49a169c
Type: security-commit

## Details
Fix permitBatchAndCall reentrancy attack (#1110)

## Patch
### pkg/pool-hooks/contracts/MinimalRouter.sol
```diff
@@ -11,13 +11,9 @@ import { IWETH } from "@balancer-labs/v3-interfaces/contracts/solidity-utils/mis
 import { IVault } from "@balancer-labs/v3-interfaces/contracts/vault/IVault.sol";
 import "@balancer-labs/v3-interfaces/contracts/vault/VaultTypes.sol";
 
-import {
-    ReentrancyGuardTransient
-} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
-
 import { RouterCommon } from "@balancer-labs/v3-vault/contracts/RouterCommon.sol";
 
-abstract contract MinimalRouter is RouterCommon, ReentrancyGuardTransient {
+abstract contract MinimalRouter is RouterCommon {
     using Address for address payable;
     using SafeCast for *;
 
```

### pkg/vault/contracts/BatchRouter.sol
```diff
@@ -15,9 +15,6 @@ import "@balancer-labs/v3-interfaces/contracts/vault/VaultTypes.sol";
 import { EVMCallModeHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/EVMCallModeHelpers.sol";
 import { CastingHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/CastingHelpers.sol";
 import { InputHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/InputHelpers.sol";
-import {
-    ReentrancyGuardTransient
-} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
 import {
     TransientEnumerableSet
 } from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/TransientEnumerableSet.sol";
@@ -38,7 +35,7 @@ struct SwapStepLocals {
  * These interpret the steps and paths in the input data, perform token accounting (in transient storage, to save gas),
  * settle with the Vault, and handle wrapping and unwrapping ETH.
  */
-contract BatchRouter is IBatchRouter, BatchRouterCommon, ReentrancyGuardTransient {
+contract BatchRouter is IBatchRouter, BatchRouterCommon {
     using CastingHelpers for *;
     using TransientEnumerableSet for TransientEnumerableSet.AddressSet;
     using TransientStorageHelpers for *;
```

### pkg/vault/contracts/CompositeLiquidityRouter.sol
```diff
@@ -13,9 +13,6 @@ import "@balancer-labs/v3-interfaces/contracts/vault/VaultTypes.sol";
 
 import { EVMCallModeHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/EVMCallModeHelpers.sol";
 import { InputHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/InputHelpers.sol";
-import {
-    ReentrancyGuardTransient
-} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
 import {
     TransientEnumerableSet
 } from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/TransientEnumerableSet.sol";
@@ -31,7 +28,7 @@ import { BatchRouterCommon } from "./BatchRouterCommon.sol";
  * These execute the steps needed to add to and remove liquidity from these special types of pools, and settle
  * the operation with the Vault.
  */
-contract CompositeLiquidityRouter is ICompositeLiquidityRouter, BatchRouterCommon, ReentrancyGuardTransient {
+contract CompositeLiquidityRouter is ICompositeLiquidityRouter, BatchRouterCommon {
     using TransientEnumerableSet for TransientEnumerableSet.AddressSet;
     using TransientStorageHelpers for *;
 
```

### pkg/vault/contracts/Router.sol
```diff
@@ -13,18 +13,14 @@ import { IRouter } from "@balancer-labs/v3-interfaces/contracts/vault/IRouter.so
 import { IVault } from "@balancer-labs/v3-interfaces/contracts/vault/IVault.sol";
 import "@balancer-labs/v3-interfaces/contracts/vault/VaultTypes.sol";
 
-import {
-    ReentrancyGuardTransient
-} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
-
 import { RouterCommon } from "./RouterCommon.sol";
 
 /**
  * @notice Entrypoint for swaps, liquidity operations, and corresponding queries.
  * @dev The external API functions unlock the Vault, which calls back into the corresponding hook functions.
  * These interact with the Vault, transfer tokens, settle accounting, and handle wrapping and unwrapping ETH.
  */
-contract Router is IRouter, RouterCommon, ReentrancyGuardTransient {
+contract Router is IRouter, RouterCommon {
     using Address for address payable;
     using SafeCast for *;
 
```

### pkg/vault/contracts/RouterCommon.sol
```diff
@@ -15,6 +15,9 @@ import { IAllowanceTransfer } from "permit2/src/interfaces/IAllowanceTransfer.so
 import { IVault } from "@balancer-labs/v3-interfaces/contracts/vault/IVault.sol";
 
 import { StorageSlotExtension } from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/StorageSlotExtension.sol";
+import {
+    ReentrancyGuardTransient
+} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
 import { InputHelpers } from "@balancer-labs/v3-solidity-utils/contracts/helpers/InputHelpers.sol";
 import { RevertCodec } from "@balancer-labs/v3-solidity-utils/contracts/helpers/RevertCodec.sol";
 import { Version } from "@balancer-labs/v3-solidity-utils/contracts/helpers/Version.sol";
@@ -30,7 +33,7 @@ import { VaultGuard } from "./VaultGuard.sol";
  * Vault is the Router contract itself, not the account that invoked the Router), versioning, and the external
  * invocation functions (`permitBatchAndCall` and `multicall`).
  */
-abstract contract RouterCommon is IRouterCommon, VaultGuard, Version {
+abstract contract RouterCommon is IRouterCommon, VaultGuard, ReentrancyGuardTransient, Version {
     using TransientStorageHelpers for StorageSlotExtension.Uint256SlotType;
     using Address for address payable;
     using StorageSlotExtension for *;
@@ -152,7 +155,19 @@ abstract contract RouterCommon is IRouterCommon, VaultGuard, Version {
         IAllowanceTransfer.PermitBatch calldata permit2Batch,
         bytes calldata permit2Signature,
         bytes[] calldata multicallData
-    ) external payable virtual saveSender(msg.sender) returns (bytes[] memory results) {
+    ) external payable virtual returns (bytes[] memory results) {
+        _permitBatch(permitBatch, permitSignatures, permit2Batch, permit2Signature);
+
+        // Execute all the required operations once permissions have been granted.
+        return multicall(multicallData);
+    }
+
+    function _permitBatch(
+        PermitApproval[] calldata permitBatch,
+        bytes[] calldata permitSignatures,
+        IAllowanceTransfer.PermitBatch calldata permit2Batch,
+        bytes calldata permit2Signature
+    ) internal nonReentrant {
         InputHelpers.ensureInputLengthMatch(permitBatch.length, permitSignatures.length);
 
         // Use Permit (ERC-2612) to grant allowances to Permit2 for tokens to swap,
@@ -193,9 +208,6 @@ abstract contract RouterCommon is IRouterCommon, VaultGuard, Version {
             // Use Permit2 for tokens that are swapped and added into the Vault.
             _permit2.permit(msg.sender, permit2Batch, permit2Signature);
         }
-
-        // Execute all the required operations once permissions have been granted.
-        return multicall(multicallData);
     }
 
     /// @inheritdoc IRouterCommon
```

### pkg/vault/contracts/test/RouterCommonMock.sol
```diff
@@ -2,6 +2,7 @@
 
 pragma solidity ^0.8.24;
 
+import { IAllowanceTransfer } from "permit2/src/interfaces/IAllowanceTransfer.sol";
 import { IPermit2 } from "permit2/src/interfaces/IPermit2.sol";
 import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
 
@@ -71,4 +72,13 @@ contract RouterCommonMock is RouterCommon {
     function assertETHBalance() public payable {
         require(address(msg.sender).balance > 0, "Balance must be more then 0");
     }
+
+    function manualPermitBatchReentrancy(
+        PermitApproval[] calldata permitBatch,
+        bytes[] calldata permitSignatures,
+        IAllowanceTransfer.PermitBatch calldata permit2Batch,
+        bytes calldata permit2Signature
+    ) public nonReentrant {
+        _permitBatch(permitBatch, permitSignatures, permit2Batch, permit2Signature);
+    }
 }
```

### pkg/vault/test/.contract-sizes/BatchRouter
```diff
@@ -1,2 +1,2 @@
-Bytecode	17.600
-InitCode	19.397
\ No newline at end of file
+Bytecode	17.570
+InitCode	19.361
\ No newline at end of file
```

### pkg/vault/test/.contract-sizes/CompositeLiquidityRouter
```diff
@@ -1,2 +1,2 @@
-Bytecode	21.971
-InitCode	23.834
\ No newline at end of file
+Bytecode	21.947
+InitCode	23.804
\ No newline at end of file
```

### pkg/vault/test/.contract-sizes/Router
```diff
@@ -1,2 +1,2 @@
-Bytecode	24.055* (56 over)
-InitCode	25.407
\ No newline at end of file
+Bytecode	24.025* (26 over)
+InitCode	25.371
\ No newline at end of file
```

### pkg/vault/test/foundry/RouterCommon.t.sol
```diff
@@ -6,10 +6,15 @@ import "forge-std/Test.sol";
 
 import { SafeCast } from "@openzeppelin/contracts/utils/math/SafeCast.sol";
 import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
+import { IAllowanceTransfer } from "permit2/src/interfaces/IAllowanceTransfer.sol";
 
+import { IRouterCommon } from "@balancer-labs/v3-interfaces/contracts/vault/IRouterCommon.sol";
 import { IVault } from "@balancer-labs/v3-interfaces/contracts/vault/IVault.sol";
 
 import { ReentrancyAttack } from "@balancer-labs/v3-solidity-utils/contracts/test/ReentrancyAttack.sol";
+import {
+    ReentrancyGuardTransient
+} from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/ReentrancyGuardTransient.sol";
 import { StorageSlotExtension } from "@balancer-labs/v3-solidity-utils/contracts/openzeppelin/StorageSlotExtension.sol";
 
 import { BaseVaultTest } from "./utils/BaseVaultTest.sol";
@@ -184,6 +189,16 @@ contract RouterCommonTest is BaseVaultTest {
         assertEq(balanceAfter, balanceBefore, "Value wasn't returned");
     }
 
+    function testPermitBatchReentrancy() public {
+        IRouterCommon.PermitApproval[] memory permitBatch;
+        bytes[] memory permitSignatures;
+        IAllowanceTransfer.PermitBatch memory permit2Batch;
+        bytes memory permit2Signature;
+
+        vm.expectRevert(ReentrancyGuardTransient.ReentrancyGuardReentrantCall.selector);
+        routerMock.manualPermitBatchReentrancy(permitBatch, permitSignatures, permit2Batch, permit2Signature);
+    }
+
     struct EthStateTest {
         uint256 bobEthBefore;
         uint256 bobEthAfter;
```
