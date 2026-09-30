# [?] jit audit fixes: Remaining ReentrancyGuard Import

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-09-16
Source: https://github.com/gmx-io/gmx-synthetics/commit/1000ff911c707f4ba89e696502cfa40979f4d39f
Type: security-commit

## Details
jit audit fixes: Remaining ReentrancyGuard Import

## Patch
### contracts/exchange/JitOrderHandler.sol
```diff
@@ -2,8 +2,6 @@
 
 pragma solidity ^0.8.0;
 
-import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
-
 import "../glv/glvShift/GlvShiftUtils.sol";
 import "./BaseOrderHandler.sol";
 import "../oracle/Oracle.sol";
```
