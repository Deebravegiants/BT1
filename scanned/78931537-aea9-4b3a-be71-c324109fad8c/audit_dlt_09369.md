# [?] Fix reentrancy attack in multicall  (#1103)

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2024-11-13
Source: https://github.com/balancer/balancer-v3-monorepo/commit/4e8c3bb725e3caf79777c448c971dcfbba801d8f
Type: security-commit

## Details
Fix reentrancy attack in multicall  (#1103)

## Patch
### pkg/vault/contracts/RouterCommon.sol
```diff
@@ -106,8 +106,9 @@ abstract contract RouterCommon is IRouterCommon, VaultGuard, Version {
         _;
         _isReturnEthLockedSlot().tstore(false);
 
-        _returnEth(_getSenderSlot().tload());
+        address sender = _getSenderSlot().tload();
         _discardSenderIfRequired(isExternalSender);
+        _returnEth(sender);
     }
 
     function _saveSender(address sender) internal returns (bool isExternalSender) {
```

### pkg/vault/test/.contract-sizes/BatchRouter
```diff
@@ -1,2 +1,2 @@
-Bytecode	17.544
-InitCode	19.342
\ No newline at end of file
+Bytecode	17.548
+InitCode	19.346
\ No newline at end of file
```

### pkg/vault/test/.contract-sizes/CompositeLiquidityRouter
```diff
@@ -1,2 +1,2 @@
-Bytecode	21.842
-InitCode	23.698
\ No newline at end of file
+Bytecode	21.846
+InitCode	23.702
\ No newline at end of file
```

### pkg/vault/test/.contract-sizes/Router
```diff
@@ -1,2 +1,2 @@
-Bytecode	23.999
-InitCode	25.352
\ No newline at end of file
+Bytecode	24.003* (3 over)
+InitCode	25.355
\ No newline at end of file
```

### pkg/vault/test/.contract-sizes/VaultExtension
```diff
@@ -1,2 +1,2 @@
-Bytecode	19.350
-InitCode	20.495
\ No newline at end of file
+Bytecode	19.771
+InitCode	20.924
\ No newline at end of file
```

### pkg/vault/test/gas/.hardhat-snapshots/[PoolMock - WithNestedPool - BatchRouter] swap exact in - reverse - tokenD-tokenA
```diff
@@ -1 +1 @@
-510.4k
\ No newline at end of file
+510.5k
\ No newline at end of file
```

### pkg/vault/test/gas/.hardhat-snapshots/[PoolMockWithHooks - WithNestedPool - BatchRouter] swap exact in - reverse - tokenD-tokenA
```diff
@@ -1 +1 @@
-560.2k
\ No newline at end of file
+560.4k
\ No newline at end of file
```
