# [?] fix spelling on reentrancyLock

## Summary
Severity: Unknown
Chain: Uniswap
Component: Uniswap/v3-core
Published: 2019-10-02
Source: https://github.com/Uniswap/v3-core/commit/3512a8af16389a748c7a07b3462b6dac5677fc5d
Type: security-commit

## Details
fix spelling on reentrancyLock

## Patch
### contracts/UniswapERC20.sol
```diff
@@ -27,13 +27,13 @@ contract UniswapERC20 is ERC20 {
 
   mapping (address => TokenData) public dataForToken;
 
-  bool private rentrancyLock = false;
+  bool private reentrancyLock = false;
 
   modifier nonReentrant() {
-    require(!rentrancyLock);
-    rentrancyLock = true;
+    require(!reentrancyLock);
+    reentrancyLock = true;
     _;
-    rentrancyLock = false;
+    reentrancyLock = false;
   }
 
 
```
