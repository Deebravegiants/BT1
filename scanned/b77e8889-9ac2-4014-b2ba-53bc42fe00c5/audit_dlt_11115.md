# [?] initializing reentrancy guard in constructor

## Summary
Severity: Unknown
Chain: zkSync Lite
Component: matter-labs/zksync
Published: 2021-11-09
Source: https://github.com/matter-labs/zksync/commit/c9da4d6e4bf62282a6fcc258471090fa3be6b3f2
Type: security-commit

## Details
initializing reentrancy guard in constructor

## Patch
### contracts/contracts/DeployFactory.sol
```diff
@@ -40,8 +40,6 @@ contract DeployFactory is TokenDeployInit {
         require(_governor != address(0), "governor check");
         require(_feeAccountAddress != address(0), "fee acc address check");
 
-        ZkSync(_zkSyncTarget).initialize(abi.encode(address(0), address(0), address(0), bytes32(0)));
-
         deployProxyContracts(_govTarget, _verifierTarget, _zkSyncTarget, _genesisRoot, _firstValidator, _governor);
 
         selfdestruct(msg.sender);
```

### contracts/contracts/ZkSync.sol
```diff
@@ -118,6 +118,10 @@ contract ZkSync is UpgradeableMaster, Storage, Config, Events, ReentrancyGuard {
         return !exodusMode;
     }
 
+    constructor() {
+        initializeReentrancyGuard();
+    }
+
     /// @notice zkSync contract initialization. Can be external because Proxy contract intercepts illegal calls of this function.
     /// @param initializationParameters Encoded representation of initialization parameters:
     /// @dev _governanceAddress The address of Governance contract
```
