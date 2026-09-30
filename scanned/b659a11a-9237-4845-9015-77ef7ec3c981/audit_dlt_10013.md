# [?] Address review: bound balance as uint256, sound receive-side overflow require, drop redundant per-rule bounds

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2026-07-23
Source: https://github.com/morpho-org/morpho-blue/commit/6b4653a7ad9e9129b61201f52cc22a14454ffc75
Type: security-commit

## Details
Address review: bound balance as uint256, sound receive-side overflow require, drop redundant per-rule bounds

## Patch
### certora/specs/Liveness.spec
```diff
@@ -35,21 +35,17 @@ function summaryId(MorphoInternalAccess.MarketParams marketParams) returns Morph
 }
 
 function summarySafeTransferFrom(address token, address from, address to, uint256 amount) {
-    // Safe requires: transferred amounts and the singleton's token balances are bounded by Morpho's uint128
-    // accounting, and a balance is non-negative. These are structural facts about the ghost (a mathint that
-    // stands in for a real, non-negative, bounded token balance), not the liveness precondition. The
-    // "singleton holds enough tokens" assumption (balance[token] >= amount) is still a proof obligation of the
-    // assert below, discharged by an explicit require in each rule.
-    require amount < 2^128;
+    // Safe requires because a token balance is a non-negative uint256 (it can exceed 2^128, as a token may be shared across markets).
     require balance[token] >= 0;
-    require balance[token] < 2^128;
+    require balance[token] <= max_uint256;
     if (from == currentContract) {
-        // Assert (not require) so that the absence of underflow is a proof obligation, discharged by the
-        // per-rule assumption that the singleton holds enough tokens (e.g. balance[token] >= totalSupplyAssets(id)).
+        // Assert so that the absence of underflow is a proof obligation.
         balance[token] = assert_uint256(balance[token] - amount);
     }
     if (to == currentContract) {
-        // Assert (not require) so that the absence of overflow is a proof obligation, discharged by the bounds above.
+        // Safe require because an erc20's total supply, which is the sum of balances, fits in uint256.
+        require amount <= max_uint256 - balance[token];
+        // Assert (not require) so that the absence of overflow is a proof obligation.
         balance[token] = assert_uint256(balance[token] + amount);
     }
 }
@@ -88,8 +84,6 @@ rule supplyChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams marke
     require currentContract != e.msg.sender;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
-    require balance[marketParams.loanToken] < 2^128;
 
     mathint sharesBefore = supplyShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -114,8 +108,6 @@ rule supplyChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams marke
 rule canSupplyByPassingShares(env e, MorphoInternalAccess.MarketParams marketParams, uint256 shares, address onBehalf, bytes data) {
     // Safe require because Morpho cannot call such functions by itself.
     require currentContract != e.msg.sender;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
-    require balance[marketParams.loanToken] < 2^128;
     uint256 suppliedAssets;
     suppliedAssets, _ = supply(e, marketParams, 0, shares, onBehalf, data);
 
@@ -214,8 +206,6 @@ rule repayChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams market
     require currentContract != e.msg.sender;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
-    require balance[marketParams.loanToken] < 2^128;
 
     mathint sharesBefore = borrowShares(id, onBehalf);
     mathint balanceBefore = balance[marketParams.loanToken];
@@ -243,8 +233,6 @@ rule repayChangesTokensAndShares(env e, MorphoInternalAccess.MarketParams market
 rule canRepayByPassingShares(env e, MorphoInternalAccess.MarketParams marketParams, uint256 shares, address onBehalf, bytes data) {
     // Safe require because Morpho cannot call such functions by itself.
     require currentContract != e.msg.sender;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
-    require balance[marketParams.loanToken] < 2^128;
     uint256 repaidAssets;
     repaidAssets, _ = repay(e, marketParams, 0, shares, onBehalf, data);
 
@@ -257,8 +245,6 @@ rule supplyCollateralChangesTokensAndBalance(env e, MorphoInternalAccess.MarketP
 
     // Safe require because Morpho cannot call such functions by itself.
     require currentContract != e.msg.sender;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving tokens.
-    require balance[marketParams.collateralToken] < 2^128;
 
     mathint collateralBefore = collateral(id, onBehalf);
     mathint balanceBefore = balance[marketParams.collateralToken];
@@ -306,8 +292,6 @@ rule liquidateChangesTokens(env e, MorphoInternalAccess.MarketParams marketParam
     require marketParams.loanToken != marketParams.collateralToken;
     // Assumption to ensure that no interest is accumulated.
     require lastUpdate(id) == e.block.timestamp;
-    // Assume that tokens have bounded supply, so the loan token balance cannot overflow when receiving the repaid assets.
-    require balance[marketParams.loanToken] < 2^128;
     // Assume that the singleton holds enough collateral tokens to cover the seized assets (which are at most the borrower's collateral).
     // Justified by the idleAmountLessThanBalance invariant (ConsistentState.spec): balance[token] >= idleAmount[token] >= collateral.
     require balance[marketParams.collateralToken] >= to_mathint(collateral(id, borrower));
@@ -341,8 +325,6 @@ rule canLiquidateByPassingShares(env e, MorphoInternalAccess.MarketParams market
     MorphoInternalAccess.Id id = Util.libId(marketParams);
     // Safe require because Morpho cannot call such functions by itself.
     require currentContract != e.msg.sender;
-    // Assume that tokens have bounded supply, so the loan token balance cannot overflow when receiving the repaid assets.
-    require balance[marketParams.loanToken] < 2^128;
     // Assume that the singleton holds enough collateral tokens to cover the seized assets (at most the borrower's collateral).
     require balance[marketParams.collateralToken] >= to_mathint(collateral(id, borrower));
     uint256 seizedAssets;
@@ -391,8 +373,6 @@ rule canRepayAll(env e, MorphoInternalAccess.MarketParams marketParams, uint256
 
     // Assume that the invariant about tokens total supply is respected.
     require totalBorrowAssets(id) < 10^35;
-    // Assume that tokens have bounded supply, so the singleton balance cannot overflow when receiving the repaid assets.
-    require balance[marketParams.loanToken] < 2^128;
 
     repay@withrevert(e, marketParams, 0, shares, e.msg.sender, data);
 
```
