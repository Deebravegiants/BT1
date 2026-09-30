# [?] add reentrancy guard to fromController functions

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-07-21
Source: https://github.com/gmx-io/gmx-synthetics/commit/ab5a783e6214b7b2ebf98c9081b8f9d15657c1a3
Type: security-commit

## Details
add reentrancy guard to fromController functions

## Patch
### contracts/exchange/DepositHandler.sol
```diff
@@ -2,6 +2,8 @@
 
 pragma solidity ^0.8.0;
 
+import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
+
 import "./BaseHandler.sol";
 
 import "../market/Market.sol";
@@ -18,7 +20,7 @@ import "./IDepositHandler.sol";
 
 // @title DepositHandler
 // @dev Contract to handle creation, execution and cancellation of deposits
-contract DepositHandler is IDepositHandler, BaseHandler {
+contract DepositHandler is IDepositHandler, BaseHandler, ReentrancyGuard {
     using Deposit for Deposit.Props;
 
     DepositVault public immutable depositVault;
@@ -134,7 +136,7 @@ contract DepositHandler is IDepositHandler, BaseHandler {
     function executeDepositFromController(
         IExecuteDepositUtils.ExecuteDepositParams calldata executeDepositParams,
         Deposit.Props calldata deposit
-    ) external onlyController returns (uint256) {
+    ) external nonReentrant onlyController returns (uint256) {
         FeatureUtils.validateFeature(dataStore, Keys.executeDepositFeatureDisabledKey(address(this)));
         return ExecuteDepositUtils.executeDeposit(executeDepositParams, deposit);
     }
```

### contracts/exchange/WithdrawalHandler.sol
```diff
@@ -2,6 +2,8 @@
 
 pragma solidity ^0.8.0;
 
+import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
+
 import "./BaseHandler.sol";
 import "../error/ErrorUtils.sol";
 
@@ -17,7 +19,7 @@ import "./IWithdrawalHandler.sol";
 
 // @title WithdrawalHandler
 // @dev Contract to handle creation, execution and cancellation of withdrawals
-contract WithdrawalHandler is IWithdrawalHandler, BaseHandler {
+contract WithdrawalHandler is IWithdrawalHandler, BaseHandler, ReentrancyGuard {
     using Withdrawal for Withdrawal.Props;
 
     MultichainVault public immutable multichainVault;
@@ -132,7 +134,7 @@ contract WithdrawalHandler is IWithdrawalHandler, BaseHandler {
     function executeWithdrawalFromController(
         IExecuteWithdrawalUtils.ExecuteWithdrawalParams calldata executeWithdrawalParams,
         Withdrawal.Props calldata withdrawal
-    ) external onlyController returns (IExecuteWithdrawalUtils.ExecuteWithdrawalResult memory) {
+    ) external nonReentrant onlyController returns (IExecuteWithdrawalUtils.ExecuteWithdrawalResult memory) {
         FeatureUtils.validateFeature(dataStore, Keys.executeWithdrawalFeatureDisabledKey(address(this)));
         return ExecuteWithdrawalUtils.executeWithdrawal(executeWithdrawalParams, withdrawal);
     }
```
