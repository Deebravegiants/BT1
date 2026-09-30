# [?] Fix unsound require assumptions in Liveness spec (#781)

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2026-07-23
Source: https://github.com/morpho-org/morpho-blue/commit/2a2921ab0ff90d59e6e9ea31437d00c0a7b844e5
Type: security-commit

## Details
Fix unsound require assumptions in Liveness spec (#781)

In summarySafeTransferFrom, the ghost balance under/overflow was silenced
with require_uint256, which is unsound in liveness rules (@withrevert +
assert !lastReverted): it assumes away the very no-revert precondition the
rules aim to prove.

Switch both branches to assert_uint256, turning the hidden assumption into
a proof obligation, and add the explicit, justified assumptions each rule
now needs (singleton solvency for out-transfers, bounded supply for
in-transfers).

Fixes #781

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_013Kx6WMx5o6emArfUMRXERr

## Patch
### certora/specs/Liveness.spec
```diff
@@ -36,12 +36,14 @@ function summaryId(MorphoInternalAccess.MarketParams marketParams) returns Morph
 
 function summarySafeTransferFrom(address token, address from, address to, uint256 amount) {
     if (from == currentContract) {
-        // Safe require because the reference implementation would revert.
-        balance[token] = require_uint256(balance[token] - amount);
+        // Assert instead of require so that the absence of underflow is a proof obligation, discharged by
+        // an explicit assumption in each rule (e.g. that the singleton holds enough tokens: balance[token] >= amount).
+        balance[token] = assert_uint256(balance[token] - amount);
     }
     if (to == currentContract) {
-        // Safe require because the reference implementation would revert.
-        balance[token] = require_uint256(balance[token] + amount);
+        // Assert instead of require so that the absence of overflow is a proof obligation, discharged by
+        // an explicit assumption in each rule (e.g. that tokens have bounded supply: balance[token] cannot overflow).
+        balance[token] = assert_uint256(balance[token] + amount);
     }
 }
 
@@ -79,6 +81,8 @@ rule supplyChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams marke
     require currentContract != e.msg.sender;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
+    require balance[marketParams.loanToken] < 2^128;
 
     mathint sharesBefore = supplyShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -115,6 +119,9 @@ rule withdrawChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams mar
     require currentContract != receiver;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that the singleton holds enough loan tokens to cover the withdrawal (which is at most totalSupplyAssets).
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= totalSupplyAssets.
+    require balance[marketParams.loanToken] >= to_mathint(totalSupplyAssets(id));
 
     mathint sharesBefore = supplyShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -151,6 +158,9 @@ rule borrowChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams marke
     require currentContract != receiver;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that the singleton holds enough loan tokens to cover the borrow (which is at most totalSupplyAssets).
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= totalSupplyAssets.
+    require balance[marketParams.loanToken] >= to_mathint(totalSupplyAssets(id));
 
     mathint sharesBefore = borrowShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -187,6 +197,8 @@ rule repayChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams market
     require currentContract != e.msg.sender;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
+    require balance[marketParams.loanToken] < 2^128;
 
     mathint sharesBefore = borrowShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -224,6 +236,8 @@ rule supplyCollateralChangesTokensAndBalance(env e, MorphoInternalAccess.MarketP
 
     // Safe require because Morpho cannot call such functions by itself.
     require currentContract != e.msg.sender;
+    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
+    require balance[marketParams.collateralToken] < 2^128;
 
     mathint collateralBefore = collateral(id, onBehalf);
     mathint balanceBefore = balance[marketParams.collateralToken];
@@ -245,6 +259,9 @@ rule withdrawCollateralChangesTokensAndBalance(env e, MorphoInternalAccess.Marke
     require currentContract != receiver;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that the singleton holds enough collateral tokens to cover the withdrawal.
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= assets.
+    require balance[marketParams.collateralToken] >= to_mathint(assets);
 
     mathint collateralBefore = collateral(id, onBehalf);
     mathint balanceBefore = balance[marketParams.collateralToken];
@@ -268,6 +285,11 @@ rule liquidateChangesTokens(env e, MorphoInternalAccess.MarketParams marketParam
     require marketParams.loanToken != marketParams.collateralToken;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
+    // Assume that tokens have bounded supply, so the loan token balance cannot overflow when receiving the repaid assets.
+    require balance[marketParams.loanToken] < 2^128;
+    // Assume that the singleton holds enough collateral tokens to cover the seized assets (which are at most the borrower's collateral).
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= collateral.
+    require balance[marketParams.collateralToken] >= to_mathint(collateral(id, borrower));
 
     mathint collateralBefore = collateral(id, borrower);
     mathint balanceLoanBefore = balance[marketParams.loanToken];
@@ -339,6 +361,8 @@ rule canRepayAll(env e, MorphoInternalAccess.MarketParams marketParams, uint256
 
     // Assume that the invariant about tokens total supply is respected.
     require totalBorrowAssets(id) < 10^35;
+    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving the repaid assets.
+    require balance[marketParams.loanToken] < 2^128;
 
     repay@withrevert(e, marketParams, 0, shares, e.msg.sender, data);
 
@@ -363,6 +387,9 @@ rule canWithdrawAll(env e, MorphoInternalAccess.MarketParams marketParams, uint2
     require lastUpdate(id) <= e.block.timestamp;
     // Safe require because of the sumSupplySharesCorrect invariant.
     require shares <= totalSupplyShares(id);
+    // Assume that the singleton holds enough loan tokens to cover the withdrawal (which is at most totalSupplyAssets).
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= totalSupplyAssets.
+    require balance[marketParams.loanToken] >= to_mathint(totalSupplyAssets(id));
 
     withdraw@withrevert(e, marketParams, 0, shares, e.msg.sender, receiver);
 
@@ -385,6 +412,9 @@ rule canWithdrawCollateralAll(env e, MorphoInternalAccess.MarketParams marketPar
     require lastUpdate(id) <= e.block.timestamp;
     // Assume that the user does not have an outstanding debt.
     require borrowShares(id, e.msg.sender) == 0;
+    // Assume that the singleton holds enough collateral tokens to cover the withdrawal.
+    // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= assets.
+    require balance[marketParams.collateralToken] >= to_mathint(assets);
 
     withdrawCollateral@withrevert(e, marketParams, assets, e.msg.sender, receiver);
 
```
